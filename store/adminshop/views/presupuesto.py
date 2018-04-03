# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   28-Aug-2017
# @Email:  valle.mrv@gmail.com
# @Filename: views.py
# @Last modified by:   valle
# @Last modified time: 16-Jan-2018
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
from adminshop.forms import CPClientesForm, PRProductoForms
from adminshop.models import (Productos, Presupuesto, LineasPresupuesto, Historial,
                              Reparaciones, Clientes, ConfigSite, Firmas)
from django.template.loader import get_template
#from django.template import Context
from . import validoDNI, get_first_direccion, set_first_direccion
from adminshop.utility import get_documento_venta, get_documento_presupuesto
from tokenapi.http import JsonResponse, JsonError
from reportlab.graphics.barcode import code39, code128, code93
from adminshop.utility import save_historial
import threading
import base64
import json
import trml2pdf
import os

# Create your views here.
@login_required(login_url='login_tk')
def presupuesto_find_cliente(request):
    vaciar_session_press(request)
    if request.method == "POST" and "DNI" in request.POST:
        if validoDNI(request.POST["DNI"]):
            return presupuesto_clientes(request)
        else:
            return render(request, 'tienda/compras/find_cliente.html',{
                "mensaje": "DNI no valido"
            })

    return render(request, 'tienda/compras/find_cliente.html')

@login_required(login_url='login_tk')
def find_actuacion(request):
    codigo = request.POST['codigo']
    datos = Reparaciones.objects.filter(Q(detalle__contains=codigo) |
                                        Q(codigo__contains=codigo))

    return render(request, "tienda/presupuestos/lista_actuaciones.html",
                      {'query': datos})

@login_required(login_url='login_tk')
def find_presupuesto(request):
    filter = request.POST["filter"]
    if filter != "" and filter[0] in ["P", "p"] :
        filter = filter[1:]
        facturas  = Presupuesto.objects.filter(Q(pk=filter))
    else:
        facturas  = Presupuesto.objects.filter(Q(fecha__contains=filter)|
                                               Q(cliente__DNI__contains=filter)|
                                               Q(cliente__nombre_completo__contains=filter))
    return render(request, 'tienda/presupuestos/listado_ajax.html',{
        "facturas": facturas
    })



@login_required(login_url='login_tk')
def cancelar_presupuesto(request, pg="/listado_productos/PS"):
    pr  = Presupuesto.objects.get(pk=request.session["accion_presupuesto_pk"])
    pr.producto.estado = "CT"
    pr.producto.save()
    pr.delete()
    Firmas.objects.filter(Q(documento_id=pr.pk) &
                          Q(tipo_documento="RP")).delete()
    vaciar_session_press(request)
    return redirect(pg)

@login_required(login_url='login_tk')
def lista_presupuestos(request):
    facturas  = Presupuesto.objects.all()
    return render(request, 'tienda/presupuestos/listado.html',{
        "facturas": facturas
    })

@login_required(login_url='login_tk')
def send_firma_press_insitu(request, id_producto, estado):
    press = Presupuesto.objects.filter(producto_id=id_producto)
    if len(press) > 0:
        id_pres = press[0].pk
    else:
        id_pres = -1
    firma = Firmas()
    firma.empleado_id = request.user.pk
    firma.documento_id = id_pres
    firma.tipo_documento = "RP"
    firma.save()
    return redirect("lista_productos", estado=estado)

@login_required(login_url='login_tk')
def get_actuacion(request):
    codigo = request.POST['codigo']
    datos = {}
    try:
        r = Reparaciones.objects.get(codigo=codigo)
    except:
        return JsonError("No se ha encontrado coincidencias")

    datos = {
        "result": True,
        "pk":r.pk,
        "codigo": r.codigo,
        "detalle": r.detalle,
        "precio": r.precio,
        "can": 1,
        "descuento": 0,
    }

    return JsonResponse(datos)

@login_required(login_url='login_tk')
def presupuesto_clientes(request):
    if request.method == 'POST':
        if len(request.POST) == 2 and "DNI" in request.POST:
            clientes = Clientes.objects.filter(DNI__contains=request.POST.get('DNI'))
            if len(clientes) > 0:
                direccion = get_first_direccion(clientes[0].id)
                full_data = dict(model_to_dict(direccion).items() + model_to_dict(clientes[0]).items())
                form = CPClientesForm (full_data, instance=clientes[0])
                titulo = 'Cliente existente'
                tipo = "presupuesto"
                request.session["accion_presupuesto_dni"] = request.POST.get('DNI')
                request.session["accion_presupuesto_pk_cliente"] = clientes[0].pk
            else:
                form = CPClientesForm(request.POST)
                titulo = 'Cliente no existe'
                tipo = "no_existe"
            return render(request, 'tienda/compras/clientes.html',
                    {'form':form, 'titulo': titulo, 'tipo': tipo} )


        if len(request.POST) > 2:
            clientes = Clientes.objects.filter(DNI__contains=request.POST.get('DNI'))
            request.session["accion_presupuesto_dni"] = request.POST.get('DNI')
            tipo = "presupuesto"
            if len(clientes) > 0:
                form = CPClientesForm(request.POST, instance=clientes[0])
            else:
                form = CPClientesForm(request.POST)

            if form.is_valid():
                cliente = form.save()
                direccion = set_first_direccion(request.POST, cliente.pk)
                direccion.cliente_id = cliente.pk
                direccion.save()
            else:
                return render(request, 'tienda/compras/clientes.html',
                        {'form':form, 'titulo': "Error al guradar el cliente",
                         'tipo': tipo, "form_error": form.errors})

            request.session["accion_presupuesto_pk_cliente"] = cliente.pk
            return render(request, 'tienda/compras/clientes.html',
                    {'form':form, 'titulo': "Cliente guardado o modificado",
                     'tipo': tipo})

    return redirect("find_cliente")

'''
    Si el cliente esta activo muestra vista de ventas
    si no la busqueda del cliente

'''
@login_required(login_url='login_tk')
def presupuesto(request):
    if "accion_presupuesto_dni" in request.session:
        if "accion_presupuesto_pk" in request.session:
            clientes = Clientes.objects.filter(DNI=request.session["accion_presupuesto_dni"])
            if len(clientes) > 0:
                cliente = clientes[0]
            else:
                cliente = Clientes()
            presupuesto = Presupuesto.objects.get(pk=request.session["accion_presupuesto_pk"])
            return render(request, 'tienda/presupuestos/presupuesto.html',
                          {"c": cliente,
                           "p": presupuesto,
                           "pg": "tienda",
                           "url": reverse("cancelar_presupuesto", args=("tienda",))
                           })
        else:
            f_producto = PRProductoForms()
            return render(request, 'tienda/presupuestos/productos.html',
                          {"form": f_producto})
    else:
        return redirect("presupuesto_find_cliente")


@login_required(login_url='login_tk')
def save_presupuesto(request):
    if request.method == "POST":
        try:
            producto = Productos.objects.get(ns_imei=request.POST["ns_imei"])
        except:
            producto = Productos()

        notas_tecnico = "" if not "notas_tecnico" in request.POST else request.POST["notas_tecnico"]
        observacion_cliente = "" if not "observacion_cliente" in request.POST else request.POST["observacion_cliente"]

        f_producto = PRProductoForms(request.POST, instance=producto)
        if f_producto.is_valid():
            producto = f_producto.save(commit=False)
            producto.estado = "PS"
            producto.es_unico = True
            producto.save()
            #Guardar el historial de la oprecion
            save_historial(request.user.pk,request.session["accion_presupuesto_pk_cliente"],
                           producto.pk, observacion_cliente )

            presupuesto = Presupuesto()
            presupuesto.cliente_id = request.session["accion_presupuesto_pk_cliente"]
            presupuesto.empleado_id = request.user.pk
            presupuesto.notas_cliente = observacion_cliente
            presupuesto.notas_tecnico = notas_tecnico
            presupuesto.producto_id = producto.pk
            presupuesto.save()
            firma = Firmas()
            firma.empleado_id = request.user.pk
            firma.documento_id = presupuesto.pk
            firma.tipo_documento = "RP"
            firma.save()
            request.session["accion_presupuesto_pk"] = presupuesto.pk
            return JsonResponse({'result': True})

    return redirect("presupuesto_find_cliente")

@login_required(login_url='login_tk')
def salir_presupuesto(request):
    vaciar_session_press(request)
    return redirect("presupuesto_find_cliente")


''' Recibe los datos del presupuesto la guarda en la base de datos,
    crea el documento pdf y lo muestra.  '''
@login_required(login_url='login_tk')
def presupuestar(request, pg="taller"):
    if request.method == "POST":
        lineas  = json.loads(request.POST["lineas"])
        pk = request.session["accion_presupuesto_pk"]
        presupuesto = Presupuesto.objects.get(pk=pk)
        presupuesto.entrega = request.POST["entrega"]
        presupuesto.save()
        producto = presupuesto.producto
        producto.estado = request.POST["estado"]
        producto.save()
        LineasPresupuesto.objects.filter(presupuesto__pk=pk).delete()
        for l in lineas:
            linea = LineasPresupuesto()
            linea.presupuesto_id = request.session["accion_presupuesto_pk"]
            linea.can = l["can"]
            linea.detalle = l["detalle"]
            linea.codigo = l["codigo"]
            linea.descuento = l["descuento"]
            linea.precio = l["total_unidad"]
            linea.save()

    url = reverse("get_presupuesto_pdf", args=[producto.pk])
    if "accion_presupuesto_by_id" in request.session:
        url = reverse("taller")
    vaciar_session_press(request)
    return HttpResponse(url)


def vaciar_session_press(request):
    if "accion_presupuesto_by_id" in request.session:
        del request.session["accion_presupuesto_by_id"]
    if "accion_presupuesto_pk" in request.session:
        del request.session["accion_presupuesto_pk"]
    if "accion_presupuesto_dni" in request.session:
        del request.session["accion_presupuesto_dni"]
    if "accion_presupuesto_pk_cliente" in request.session:
        del request.session["accion_presupuesto_pk_cliente"]

@login_required(login_url='login_tk')
def entrega_reparacion(request, id_producto):
    try:
        pres = Presupuesto.objects.filter(producto__pk=id_producto)
        cliente = Clientes()
        if len(pres) > 0:
            pres = pres[0]
            cliente = pres.cliente
    except:
        pres = Presupuesto()

    return render (request, "tienda/presupuestos/hoja_reparacion.html",
                   {"c": cliente,
                   "p": pres,
                   "tipo": "entrega"})

@login_required(login_url='login_tk')
def modificar_presupuesto(request, id_producto):
    try:
        pres = Presupuesto.objects.filter(producto__pk=id_producto)
        cliente = Clientes()
        if len(pres) > 0:
            pres = pres[0]
            cliente = pres.cliente
    except:
        pres = Presupuesto()

    return render (request, "tienda/presupuestos/hoja_reparacion.html",
                   {"c": cliente,
                   "p": pres,
                   "tipo": "modificar"})

@login_required(login_url='login_tk')
def set_entregado(request, id_producto):
    pres = Presupuesto.objects.filter(producto__pk=id_producto)
    if len(pres) > 0:
        pres = pres[0]
        cliente = pres.cliente
    producto = Productos.objects.get(pk=id_producto)
    producto.estado = "CT"
    producto.save()
    #Guardar el historial de la operación
    save_historial(request.user.pk,  cliente.pk, id_producto,
                   "Producto entregado al cliente despues de reparar")

    return redirect("lista_productos", estado='OK')


@login_required(login_url='login_tk')
def save_lineas_pres(request, id_pres):
    if request.method == "POST":
        lineas  = json.loads(request.POST["lineas"])
        presupuesto = Presupuesto.objects.get(pk=id_pres)
        LineasPresupuesto.objects.filter(presupuesto__pk=id_pres).delete()
        for l in lineas:
            linea = LineasPresupuesto()
            linea.presupuesto_id = id_pres
            linea.can = l["can"]
            linea.detalle = l["detalle"]
            linea.codigo = l["codigo"]
            linea.descuento = l["descuento"]
            linea.precio = l["total_unidad"]
            linea.save()
    return JsonResponse({"result":"success"})

# mostrar presupuesto por su ID
@login_required(login_url='login_tk')
def get_presupuesto_by_id(request, id_producto):
    presupuestos = Presupuesto.objects.filter(producto__pk=id_producto)
    if len(presupuestos) > 0:
        pre = presupuestos[0]
    else:
        Productos.objects.filter(pk=id_producto).delete()
        return redirect("lista_productos", estado="PS")

    request.session['accion_presupuesto_dni'] = pre.cliente.DNI
    request.session["accion_presupuesto_pk"] = pre.pk
    request.session["accion_presupuesto_by_id"] = True
    return redirect("presupuesto")

@login_required(login_url='login_tk')
def get_lineas_presupuesto(request, id_pres=-1):
    if "accion_presupuesto_pk" in request.session or id_pres >= 0:
        datos = []
        id_pres = id_pres if id_pres >= 0 else request.session["accion_presupuesto_pk"]
        lineas = LineasPresupuesto.objects.filter(presupuesto__pk=id_pres)
        for l in lineas:
            datos.append(model_to_dict(l))

        return JsonResponse(datos)
    else:
        return JsonResponse({'salir':True})

@login_required(login_url='login_tk')
def send_producto_rp(request, id_producto):
    producto = Productos.objects.get(pk=id_producto)
    producto.estado = "RP"
    producto.save()
    return redirect("tienda")


@login_required(login_url='login_tk')
def get_presupuesto_pdf(request, id_producto):
    presupuestos = Presupuesto.objects.filter(producto__pk=id_producto)
    if len(presupuestos) > 0:
        presupuesto = presupuestos[0]
    else:
        presupuesto = Presupuesto()
    return get_presupuesto(presupuesto)

@login_required(login_url='login_tk')
def send_presupuesto(request, id_producto):
    presupuestos = Presupuesto.objects.filter(producto__pk=id_producto)
    if len(presupuestos) > 0:
        presupuesto = presupuestos[0]
    else:
        presupuesto = Presupuesto()
    threading.Thread(target=send_presupuesto_mail, args=(presupuesto,)).start()
    return redirect("lista_presupuestos")


# para ver el documento pdf los clientes
def get_presupuesto_by_code(request, code):
    datos = json.loads(base64.b64decode(code))
    presupuesto = Presupuesto.objects.filter(pk=datos["id_presupuesto"])
    return get_presupuesto(presupuesto[0])

# crea el documento pdf y lo muestra
def get_presupuesto(pres):
    try:
        from pyPdf import PdfFileReader, PdfFileWriter
        from StringIO import StringIO
    except ImportError:
        from io import StringIO
        from PyPDF2 import PdfFileReader, PdfFileWriter

    str_output = StringIO()
    pdf_output = PdfFileWriter()
    tmpl_path = settings.DOCUMENT_TMPL
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="presupuesto_%s.pdf"' % pres.id
    doc_pres = get_documento_presupuesto(pres, pres.cliente, get_first_direccion(pres.cliente))

    if pres.factura != None:
        venta = pres.factura
        doc_venta = get_documento_venta(venta, venta.cliente, get_first_direccion(venta.cliente))
        pdf_venta = PdfFileReader(doc_venta)
        for i in range(pdf_venta.getNumPages()):
            pdf_output.addPage(pdf_venta.getPage(i))

    pdf_principal = PdfFileReader(doc_pres)
    for i in range(pdf_principal.getNumPages()):
        pdf_output.addPage(pdf_principal.getPage(i))

    pdf_output.write(str_output)
    response.write(str_output.getvalue())
    return response


def send_presupuesto_mail(pres):
    datos = {
        "id_presupuesto": pres.id,
        "id_cliente": pres.cliente.id,
        "email": pres.cliente.email,
    }
    send_data = base64.b64encode(json.dumps(datos))
    url = settings.BASE_URL+reverse("get_presupuesto_by_code", args=[send_data])
    from django.core.mail import send_mail
    from django.template.loader import render_to_string


    msg_plain = render_to_string(settings.BASE_DIR+'/templates/email/send_presupuesto.html',
                                 {'nombre': pres.cliente.nombre_completo,
                                  "url": url})
    send_mail(
        'Presupuesto',
         msg_plain,
         "info@freakmedia.es",
        [datos['email']],
     )
