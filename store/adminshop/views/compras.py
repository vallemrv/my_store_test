# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   28-Aug-2017
# @Email:  valle.mrv@gmail.com
# @Filename: views.py
# @Last modified by:   valle
# @Last modified time: 02-Mar-2018
# @License: Apache license vesion 2.0

from django.forms.models import model_to_dict
from django.db.models import Q
from django.conf import settings
from django.shortcuts import render, redirect
try:
    from django.core.urlresolvers import reverse
except ImportError:
    from django.urls import reverse

from django.contrib.auth.decorators import login_required, permission_required
from django.template.loader import render_to_string
from django.http import HttpResponse
#from django.template import Context
from django.template.loader import get_template
from adminshop.utility import get_documento_compra, get_documento_testeo
from adminshop.forms import (CPClientesForm, CPProductosForm, ProductosForm, MODProductosForm,
                             FinTratoForm, ValidarCompra, VistaValidarForm, ModelosForm)
from adminshop.models import (Modelos, Clientes, Testeo, ConfigSite, Historial, Firmas,
                              Productos, Compras, Tipos, Direcciones, DocumentoTesteo, ListaTesteo)

from adminshop.utility import save_historial, save_doc_firmas, save_doc_testeo
from . import (validoDNI, get_first_direccion, set_first_direccion)
from tokenapi.http import JsonResponse
import threading
import base64
import json
import trml2pdf
import os


@login_required(login_url='login_tk')
def get_modificar_compra(request, id_compra):
    pres = Compras.objects.filter(pk=id_compra)
    if len(pres) > 0:
        pres = pres[0]
        vendedor = pres.get_vendedor()
        producto = pres.producto
        producto_dict = model_to_dict(producto)
        producto_dict["cliente"] = vendedor['id']
        f_compra = MODProductosForm(producto_dict)
        modelo = producto.modelo

        return render (request, "tienda/compras/modificar.html",
                       {"c": vendedor,
                        "form": f_compra,
                        "m": modelo,
                        "f": pres})

    return redirect("tienda")


@login_required(login_url='login_tk')
def modificar_compra(request, id_compra):
    if request.method == "POST":
        pres = Compras.objects.filter(pk=id_compra)
        if len(pres) > 0:
            pres = pres[0]
            producto = pres.producto
            producto.tipo_id = request.POST["tipo"]
            producto.color = request.POST["color"]
            producto.modelo_id = request.POST["modelo"]
            producto.ns_imei = request.POST["ns_imei"]
            producto.precio_compra = request.POST["precio_compra"]
            producto.save()
            pres.vendedor_id = request.POST["cliente"]
            pres.save()
    return HttpResponse(reverse("listado_compras"))


@login_required(login_url='login_tk')
def ch_find_modelo(request):
    if request.method == "POST":
        filter = request.POST["filter"]
        filter_query = Modelos.objects.filter(Q(nombre__contains=filter) |
                                              Q(marca__nombre__contains=filter))
        return render(request, "tienda/compras/lista_modelos.html",
                      {'query': filter_query,
                       'change': True })

@login_required(login_url='login_tk')
def cancelar_trato(request, id_producto):
    if request.method == "POST":
        producto = Productos.objects.get(pk=id_producto)
        f_p = FinTratoForm(request.POST, instance=producto)
        if f_p.is_valid():
            p = f_p.save()
            p.estado = "CT"
            p.save()
            clientes = Historial.objects.filter(producto_id=p.pk)
            cliente_id = 1
            if len(clientes) > 0:
                cliente_id = clientes[0].cliente_id

            #guardamos un historial de la accion realizada
            save_historial(request.user.id, p.id, cliente_id,
                           "Rechazada la compra del producto..")

            vaciar_sesison_compra(request)
            return HttpResponse(reverse("tienda"))
    else:
        p = Productos.objects.get(pk=id_producto)
        p.estado = "CT"
        p.save()
        clientes = Historial.objects.filter(producto_id=p.pk)
        cliente_id = 1
        if len(clientes) > 0:
            cliente_id = clientes[0].cliente_id

        #guardamos un historial de la accion realizada
        save_historial(request.user.id, p.id, cliente_id,
                       "Rechazada la compra del producto..")

        vaciar_sesison_compra(request)
        return redirect("lista_productos", estado="TD")



@login_required(login_url='login_tk')
def validar_compra(request, id_compra):
    if request.method == "POST":
        compra = Compras.objects.get(pk=id_compra)
        f = ValidarCompra(request.POST, instance=compra)
        if f.is_valid():
            compra = f.save()
            vaciar_sesison_compra(request)

            #Guardamos el documento en la cola para ser firmado
            save_doc_firmas(request.user.pk, compra.pk, "CP")

            return redirect("tienda")
        else:
            f = VistaValidarForm(instance=compra)
            return render(request, "tienda/compras/validar_compra.html",
                          {"form": f, "form_error": f.errors })

    else:
        compra = Compras.objects.get(pk=id_compra)
        f = VistaValidarForm(instance=compra)
        return render(request, "tienda/compras/validar_compra.html",
                      {"form": f, })


@login_required(login_url='login_tk')
def send_sign(request, id_producto):
    producto = Productos.objects.get(pk=id_producto)
    compras = Compras.objects.filter(producto__id=id_producto)

    if len(compras) > 0:
        compra = compras[0]
        Firmas.objects.filter(Q(documento_id=compra.pk) &
                              Q(tipo_documento="CP")).delete()
        threading.Thread(target=send_men_sing, args=(compra,)).start()
    return render(request, "tienda/compras/sender_sign.html")


@login_required(login_url='login_tk')
def get_document_by_id(request, id_producto):
    producto = Productos.objects.get(pk=id_producto)
    compras = Compras.objects.filter(producto__id=id_producto)
    compra = Compras()
    if len(compras) > 0:
        compra = compras[0]
    return get_document(producto, compra)


@login_required(login_url='login_tk')
def find_cliente(request):
    vaciar_sesison_compra(request)
    if request.method == "POST" and "DNI" in request.POST:
        if validoDNI(request.POST["DNI"]):
            return cp_clientes(request)
        else:
            return render(request, 'tienda/compras/find_cliente.html',{
                "mensaje": "DNI no valido",
                "url_tipo": reverse("find_cliente")
            })

    return render(request, 'tienda/compras/find_cliente.html',{
        "url_tipo": reverse("find_cliente")
    })


@login_required(login_url='login_tk')
def listado_doc_testeos(request):
    testeos  = DocumentoTesteo.objects.all()
    return render(request, 'tienda/testeo/listado.html',{
        "compras": testeos
    })

@login_required(login_url='login_tk')
def find_doc_testeos(request):
    filter = request.POST["filter"]
    if len(filter) > 0 and filter[0].upper() == "T":
        filter = filter.replace("T", "")
        filter = filter.replace("t", "")
        compras  = DocumentoTesteo.objects.filter(Q(pk=filter))
    else:
        compras  = DocumentoTesteo.objects.filter(Q(cliente__DNI__contains=filter)|
                                                  Q(cliente__nombre_completo__contains=filter))
    return render(request, 'tienda/testeo/listado_ajax.html',{
        "compras": compras
    })

@login_required(login_url='login_tk')
def get_doc_testeo_by_id(request, id_doc):
    doc = DocumentoTesteo.objects.get(pk=id_doc)
    return doc_testeo(doc)


@login_required(login_url='login_tk')
def cp_clientes(request):
    if request.method == 'POST':
        if "filter" in request.POST:
            clientes = Clientes.objects.filter(DNI__icontains=request.POST.get('DNI'))
            if len(clientes) > 0:
                direccion = get_first_direccion(clientes[0].id)
                full_data = dict(model_to_dict(direccion).items() + model_to_dict(clientes[0]).items())
                form = CPClientesForm (full_data, instance=clientes[0])
                titulo = 'Cliente existente'
                tipo = "comprar"
                request.session["accion_comprar_dni"] = request.POST.get('DNI')
                request.session["accion_comprar_pk_cliente"] = clientes[0].pk
            else:
                form = CPClientesForm(request.POST)
                titulo = 'Cliente no existe'
                tipo = "no_existe"
            return render(request, 'tienda/compras/clientes_ajax.html',
                    {'form':form, 'titulo': titulo,
                     'tipo': tipo})
        elif len(request.POST) == 2 and "DNI" in request.POST:
            clientes = Clientes.objects.filter(DNI__icontains=request.POST.get('DNI'))
            if len(clientes) > 0:
                direccion = get_first_direccion(clientes[0].id)
                full_data = dict(model_to_dict(direccion).items() + model_to_dict(clientes[0]).items())
                form = CPClientesForm (full_data, instance=clientes[0])
                titulo = 'Cliente existente'
                tipo = "comprar"
                request.session["accion_comprar_dni"] = request.POST.get('DNI')
                request.session["accion_comprar_pk_cliente"] = clientes[0].pk
            else:
                form = CPClientesForm(request.POST)
                titulo = 'Cliente no existe'
                tipo = "no_existe"
            return render(request, 'tienda/compras/clientes.html',
                    {'form':form, 'titulo': titulo,
                     'tipo': tipo})


        elif len(request.POST) > 2:
            tipo = "comprar"
            clientes = Clientes.objects.filter(DNI__icontains=request.POST.get('DNI'))
            request.session["accion_comprar_dni"] = request.POST.get('DNI')
            if len(clientes) > 0:
                form = CPClientesForm(request.POST, instance=clientes[0])
            else:
                form = CPClientesForm(request.POST)

            if form.is_valid():
                cliente = form.save()
                direccion = set_first_direccion(request.POST, cliente.pk)
                if type(direccion) == Direcciones:
                    direccion.cliente_id = cliente.pk
                    direccion.save()

            else:
                return render(request, 'tienda/compras/clientes.html',
                        {'form':form, 'titulo': "Error al guardar el cliente",
                         'tipo': tipo, "form_error": form.errors})

            request.session["accion_comprar_pk_cliente"] = cliente.pk
            return render(request, 'tienda/compras/clientes.html',
                    {'form':form, 'titulo': "Cliente guardado o modificado",
                     'tipo': tipo})

    return redirect("find_cliente")

@login_required(login_url='login_tk')
def listado_compras(request):
    compras  = Compras.objects.all().exclude(tipo_vendedor="NO")
    return render(request, 'tienda/compras/listado.html',{
        "compras": compras
    })

@login_required(login_url='login_tk')
def find_compra(request):
    filter = request.POST["filter"]
    if len(filter) > 0 and "c" == filter[0].lower():
        filter = filter.replace("C", "")
        filter = filter.replace("c", "")
        compras  = Compras.objects.filter(Q(codigo_compra__icontains=filter)).exclude(vendedor_id=None)
    else:
        compras  = Compras.objects.filter(Q(codigo_compra__icontains=filter)|
                                          Q(producto__ns_imei__icontains=filter)).exclude(vendedor_id=None)
    return render(request, 'tienda/compras/listado_ajax.html',{
        "compras": compras
    })


@login_required(login_url='login_tk')
def cp_lista_modelos(request):
    if request.method == "POST":
        filter = request.POST["filter"]
        filter_query = Modelos.objects.filter(Q(nombre__icontains=filter))
        return render(request, "tienda/compras/lista_modelos.html", {'query': filter_query})


@login_required(login_url='login_tk')
def send_para_tester(request, id_modelo):
    if "accion_comprar_dni" in request.session:
        try:
            producto = Productos.objects.get(ns_imei=request.POST.get("ns_imei"))
            form = CPProductosForm(request.POST, instance=producto)
        except Exception as p:
            form = CPProductosForm(request.POST)

        if form.is_valid():
            producto = form.save(commit=False)
            producto.modelo_id = request.session["accion_comprar_pk_modelo"]
            producto.estado = "OS"
            producto.tipo_id = 1
            producto.precio_compra = producto.modelo.precio_usado
            producto.save()
            request.session["accion_comprar_pk_producto"] = producto.pk
            #Guardamos el histarial de la accion Realizada
            save_historial(request.user.pk, request.session["accion_comprar_pk_cliente"],
                           producto.pk, "Entrada para testeo posible compra")
            #Creamos el documento de recepción de terminal.
            doc = save_doc_testeo(request.user.pk, request.session["accion_comprar_pk_cliente"],
                            producto.pk)
            #Guradamos el documen to para firmar
            save_doc_firmas(request.user.pk, doc.id, "OS")
            vaciar_sesison_compra(request)
            return JsonResponse({"result": True})
    else:
        return redirect("tienda")

@login_required(login_url='login_tk')
def cp_productos(request, id_modelo=-1):
    if "accion_comprar_dni" in request.session:
        if request.method != "POST" and id_modelo < 0:
            f_modelo = ModelosForm()
            return render(request, 'tienda/compras/find_modelos.html',
                          {"form": f_modelo})
        elif request.method != "POST" and id_modelo > 0:
            request.session["accion_comprar_pk_modelo"] = id_modelo
            try:
                modelo = Modelos.objects.get(pk=id_modelo)
            except:
                modelo = Modelos()
            tipo = "no_existe"
            form = CPProductosForm()
            return render(request, 'tienda/compras/productos.html',
                          {'form':form, 'titulo': "Datos del producto",
                           'modelo': modelo,
                           'tipo': tipo})
        else:
            try:
                producto = Productos.objects.get(ns_imei=request.POST.get("ns_imei"))
                form = CPProductosForm(request.POST, instance=producto)
            except Exception as p:
                form = CPProductosForm(request.POST)

            if form.is_valid():
                producto = form.save(commit=False)
                if "accion_comprar_pk_modelo" not in request.session:
                    vaciar_sesison_compra(request)
                    return redirect("tienda")
                producto.modelo_id = request.session["accion_comprar_pk_modelo"]
                producto.estado = "TD"
                #tipos = Tipos.objects.all()
                #if len(tipos) > 0:
                #    tipo = tipos[0].pk
                #else:
                #    tipo = -1
                #producto.tipo_id = tipo
                producto.precio_compra = producto.modelo.precio_usado
                producto.save()
                request.session["accion_comprar_pk_producto"] = producto.pk
                save_historial(request.user.pk, request.session["accion_comprar_pk_cliente"],
                                     request.session["accion_comprar_pk_producto"],
                                     "Producto comprado sin testear")
                form = ProductosForm(instance=producto)
            return render(request, 'tienda/compras/compras.html',
                          {'form':form, 'titulo': "Datos del producto",
                           "form_error": form.errors,
                           "id_modelo":  request.session["accion_comprar_pk_modelo"]})
    else:
        return redirect("tienda")


@login_required(login_url='login_tk')
def calcular_precio_usado(request, id_modelo):
    if request.method == "POST":
        tipo = Tipos.objects.get(pk=request.POST["tipo"])
        modelo = Modelos.objects.get(pk=id_modelo)
        return HttpResponse("{0:.2f}".format(float(tipo.incremento)*float(modelo.precio_usado)))
    else:
        return redirect("tienda")

@login_required(login_url='login_tk')
def hacer_compra(request):
    if request.method == "POST":
        try:
            producto = Productos.objects.get(pk=request.session["accion_comprar_pk_producto"])
            producto.tipo_id = request.POST["tipo"]
            producto.precio_compra = request.POST["precio_compra"]
            producto.estado = "ST"
            producto.save()
        except Exception as error:
            return HttpResponse(reverse("en_construccion"))

        estan_todos = True
        estan_todos = estan_todos and "accion_comprar_pk_cliente" in request.session
        estan_todos = estan_todos and "accion_comprar_pk_producto" in request.session
        estan_todos = estan_todos and "accion_comprar_pk_modelo" in request.session

        if estan_todos:
            compra = guardar_compra(request.session["accion_comprar_pk_cliente"],
                                    request.session["accion_comprar_pk_producto"],
                                    request.user.id,
                                    "Realizada la compra del producto")
            return HttpResponse(reverse("validar_compra", args=[str(compra.id)]))
    else:
        return HttpResponse(reverse("tienda"))



@login_required(login_url='login_tk')
def trato_compra(request, id_producto):
    if request.method == "POST":
        producto = Productos.objects.get(pk=id_producto)
        f_p = FinTratoForm(request.POST, instance=producto)
        if f_p.is_valid():
            p = f_p.save()
            p.estado = "ST"
            p.save()
            clientes = Historial.objects.filter(producto_id=p.pk)
            cliente_id = 1
            if len(clientes) > 0:
                cliente_id = clientes[0].cliente_id
            compra = guardar_compra(cliente_id, p.id, request.user.id,
                           "Realizada la compra del producto. Despues de testear")

            return HttpResponse(reverse("validar_compra", args=[compra.id]))
    else:
        producto = Productos.objects.get(pk=id_producto)
        if producto.tipo == None:
            producto.tipo = Tipos.objects.all()[0]

        producto.precio_compra = "{0:.2f}".format(producto.modelo.precio_usado *
                                                  producto.tipo.incremento)
        producto.save()
        filter_query = Testeo.objects.filter(producto_id=id_producto)
        lista_ids = filter_query.values_list("descripcion_id", flat=True)
        no_realizaos =  ListaTesteo.objects.filter(categoria=producto.modelo.categoria)
        return render(request, "tienda/compras/trato_compra.html",
                      {'query': filter_query.exclude(estado="OK"), "p": producto,
                       "no_realizados": no_realizaos.exclude(pk__in=lista_ids),
                       "form": FinTratoForm(instance=producto)})


@login_required(login_url='login_tk')
def cancelar_compra(request):
    if request.method == "POST":
        try:
            producto = Productos.objects.get(pk=request.session["accion_comprar_pk_producto"])
            producto.tipo_id = request.POST["tipo"]
            producto.precio_compra = request.POST["precio_compra"]
            producto.estado = "CT"
            producto.save()
        except:
            return HttpResponse(reverse("tienda"))

        estan_todos = True
        estan_todos = estan_todos and "accion_comprar_pk_cliente" in request.session
        estan_todos = estan_todos and "accion_comprar_pk_producto" in request.session
        estan_todos = estan_todos and "accion_comprar_pk_modelo" in request.session

        if estan_todos:
            #Guardamos historial de la cancelacion de la comprar
            save_historial(request.user.id, request.session["accion_comprar_pk_cliente"],
                           request.session["accion_comprar_pk_producto"],
                           "Compra cancelada, producto en posesion del cliente")

            vaciar_sesison_compra(request)
            return HttpResponse(reverse("tienda"))
    else:
        return HttpResponse(reverse("en_construccion"))

@login_required(login_url='login_tk')
def salir_compra(request):
    try:
        producto = Productos.objects.get(pk=request.session["accion_comprar_pk_producto"])
        producto.estado = "CT"
        producto.save()
    except:
        pass

    vaciar_sesison_compra(request)
    return redirect("tienda")


def guardar_compra(cliente_id, producto_id, user_id, detalle):
    compra = Compras()
    compra.vendedor_id = cliente_id
    compra.tipo_vendedor = 'CL'
    compra.producto_id = producto_id
    compra.usuario_id = user_id
    compra.save()
    #Guardamos el historial
    save_historial(user_id, cliente_id, user_id, detalle)

    return compra


def vaciar_sesison_compra(request):
    if "accion_comprar_pk_cliente" in request.session:
        del request.session["accion_comprar_pk_cliente"]
    if "accion_comprar_pk_producto" in request.session:
        del request.session["accion_comprar_pk_producto"]
    if "accion_comprar_pk_modelo" in request.session:
        del request.session["accion_comprar_pk_modelo"]
    if "accion_comprar_dni" in request.session:
        del request.session["accion_comprar_dni"]

def get_document_by_code(request, code):
    datos = json.loads(base64.b64decode(code))
    compras = Compras.objects.filter(pk=datos["id_compra"])
    compra = Compras()
    if len(compras) > 0:
        compra = compras[0]
        producto = Productos.objects.get(pk=compra.producto.pk)
        return get_document(producto, compra)
    return redirect('https://google.es')

def get_document(producto, compra):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="%s.pdf"' % producto.modelo
    doc_compra = get_documento_compra(producto, compra)
    response.write(doc_compra.getvalue())
    return response

def send_men_sing(compra):
    vendedor = compra.get_vendedor()
    datos = {
        "id_compra": compra.id,
        "codigo_compra": str(compra.codigo_compra),
        "email": vendedor['email'],
    }
    send_data = base64.b64encode(json.dumps(datos))
    url = settings.BASE_URL + reverse("sign_compra", args=[send_data])
    from django.core.mail import send_mail
    from django.template.loader import render_to_string


    msg_plain = render_to_string(settings.BASE_DIR+'/templates/email/url_sign.html',
                                 {'nombre': vendedor['nombre'],
                                  "url": url})

    send_mail(
        'Firmar y aceptar condiciones',
         msg_plain,
         "info@freakmedia.es",
        [datos['email']],
     )

def sign_compra(request, code):
    datos = json.loads(base64.b64decode(code))
    compras = Compras.objects.filter(pk=datos["id_compra"])
    datos_send = None
    if len(compras) > 0:
        compra = compras[0]
        if compra.firma == '':
            vendedor = compra.get_vendedor()
            datos_send= {
                "pk": datos["id_compra"],
                "id_producto": compra.producto.pk,
                "nombre": vendedor["nombre"],
                "telefono": vendedor['telefono'],
                "DNI": vendedor["DNI"].upper(),
                "domicilio": vendedor['direccion'],
                "ns_imei": compra.producto.ns_imei,
                "precio_compra": str(compra.producto.precio_compra),
                "code": code
            }

            return render(request, "tienda/compras/sign.html", {"datos":datos_send})
        else:
            return redirect("get_document_by_code", code=code )
    return redirect('tienda')



def doc_testeo(doc):
    tmpl_path = settings.DOCUMENT_TMPL
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="testeo_%s.pdf"' % doc.producto
    pdfstr = get_documento_testeo(doc)
    response.write(pdfstr.getvalue())
    return response
