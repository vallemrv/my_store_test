# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   28-Aug-2017
# @Email:  valle.mrv@gmail.com
# @Filename: views.py
# @Last modified by:   valle
# @Last modified time: 02-Mar-2018
# @License: Apache license vesion 2.0

from django.conf import settings
from django.forms.models import model_to_dict
from django.db.models import Q
from django.shortcuts import render, redirect
try:
    from django.core.urlresolvers import reverse
except ImportError:
    from django.urls import reverse

from django.contrib.auth.decorators import login_required, permission_required
from django.template.loader import render_to_string
from django.http import HttpResponse
from adminshop.forms import (CPClientesForm)
from adminshop.models import (Clientes, Direcciones, Compras, LineasVentas, ConfigSite,
                              Productos, Ventas, Historial, Presupuesto, LineasPresupuesto)

from . import validoDNI, get_first_direccion, set_first_direccion
from adminshop.utility import save_historial, get_documento_venta, get_documento_compra
from tokenapi.http import JsonResponse, JsonError

import threading
import base64
import json

# Create your views here.
@login_required(login_url='login_tk')
def ventas_find_cliente(request):
    vaciar_session_ventas(request)
    if request.method == "POST" and "DNI" in request.POST:
        if validoDNI(request.POST["DNI"]):
            return ventas_clientes(request)
        else:
            return render(request, 'tienda/compras/find_cliente.html',{
                "mensaje": "DNI no valido",
                "url_tipo": reverse("ventas_find_cliente")
            })

    return render(request, 'tienda/compras/find_cliente.html',{
        "url_tipo": reverse("ventas_find_cliente")
    })

@login_required(login_url='login_tk')
def salir_ventas(request):
    vaciar_session_ventas(request)
    return redirect("tienda")

@login_required(login_url='login_tk')
def get_sugestion(request):
    productos = Productos.objects.filter(Q(estado__in = ["VT", "OL"]))
    send_dict = []
    for q in productos:
        send_dict.append(q.ns_imei)
    return JsonResponse(send_dict)

@login_required(login_url='login_tk')
def get_producto(request):
    ns_imei = request.POST['ns_imei']
    datos = {}
    try:
        producto = Productos.objects.filter(Q(ns_imei__icontains=ns_imei))
        producto = producto[0]
    except:
        return JsonError("No se ha encontrado coincidencias")


    compras = Compras.objects.filter(producto__pk=producto.pk)

    if len(compras) >0:
        codigo_compra = compras[0].codigo_compra
    else:
        codigo_compra = producto.id + 303450

    datos = {
        "result": True,
        "codigo_compra": codigo_compra,
        "modelo": unicode(producto),
        "ns_imei": producto.ns_imei,
        "precio": str(producto.precio_venta),
        "tipo": producto.get_descripcion_tipo(),
        "descuento": str(producto.descuento),
        "es_unico": producto.es_unico,
        "estado": producto.estado,
        "id": producto.id
    }

    return JsonResponse(datos)

@login_required(login_url='login_tk')
def ventas_clientes(request):
    if request.method == 'POST':
        if "filter" in request.POST:
            clientes = Clientes.objects.filter(DNI__icontains=request.POST.get('DNI'))
            if len(clientes) > 0:
                direccion = get_first_direccion(clientes[0].id)
                full_data = dict(model_to_dict(direccion).items() + model_to_dict(clientes[0]).items())
                form = CPClientesForm (full_data, instance=clientes[0])
                titulo = 'Cliente existente'
                tipo = "ventas"
                request.session["accion_ventas_dni"] = request.POST.get('DNI')
                request.session["accion_ventas_pk_cliente"] = clientes[0].pk
            else:
                form = CPClientesForm(request.POST)
                titulo = 'Cliente no existe'
                tipo = "no_existe"
            return render(request, 'tienda/compras/clientes_ajax.html',
                    {'form':form, 'titulo': titulo, 'tipo': tipo} )

        elif (len(request.POST) == 2 and "DNI" in request.POST):
            clientes = Clientes.objects.filter(DNI__icontains=request.POST.get('DNI'))
            if len(clientes) > 0:
                direccion = get_first_direccion(clientes[0].id)
                full_data = dict(model_to_dict(direccion).items() + model_to_dict(clientes[0]).items())
                form = CPClientesForm (full_data, instance=clientes[0])
                titulo = 'Cliente existente'
                tipo = "ventas"
                request.session["accion_ventas_dni"] = request.POST.get('DNI')
                request.session["accion_ventas_pk_cliente"] = clientes[0].pk
            else:
                form = CPClientesForm(request.POST)
                titulo = 'Cliente no existe'
                tipo = "no_existe"
            return render(request, 'tienda/compras/clientes.html',
                    {'form':form, 'titulo': titulo, 'tipo': tipo} )


        elif len(request.POST) > 2:
            clientes = Clientes.objects.filter(DNI__contains=request.POST.get('DNI'))
            request.session["accion_ventas_dni"] = request.POST.get('DNI')
            tipo = "ventas"
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

            request.session["accion_ventas_pk_cliente"] = cliente.pk
            return render(request, 'tienda/compras/clientes.html',
                    {'form':form, 'titulo': "Cliente guardado o modificado",
                     'tipo': tipo})

    return redirect("find_cliente")

@login_required(login_url='login_tk')
def find_facturas(request):
    filter = request.POST["filter"]
    if filter[0].upper() == "F":
        filter = filter.replace("F", "")
        filter = filter.replace("f", "")
        facturas  = Ventas.objects.filter(Q(pk=filter))
    else:
        facturas  = Ventas.objects.filter(Q(fecha_salida__contains=filter)|
                                          Q(cliente__DNI__contains=filter)|
                                          Q(cliente__nombre_completo__contains=filter))
    return render(request, 'tienda/ventas/listado_ajax.html',{
        "facturas": facturas
    })

@login_required(login_url='login_tk')
def listado_facturas(request):
    facturas  = Ventas.objects.all()
    return render(request, 'tienda/ventas/listado.html',{
        "facturas": facturas
    })


'''
    Si el cliente esta activo muestra vista de ventas
    si no la busqueda del cliente

'''
@login_required(login_url='login_tk')
def ventas(request):
    if "accion_ventas_dni" in request.session:
        return render(request, 'tienda/ventas/ventas.html')
    else:
        return redirect("ventas_find_cliente")


@login_required(login_url='login_tk')
def get_lineas_factura(request, id_venta):
    datos = []
    lineas = LineasVentas.objects.filter(venta__pk=id_venta)
    for l in lineas:
        productos = Productos.objects.filter(ns_imei=l.ns_imei)
        if len(productos):
            producto = productos[0]
            datos.append(
                {
                    "result": True,
                    "codigo_compra": l.codigo_compra,
                    "modelo": unicode(producto),
                    "ns_imei": producto.ns_imei,
                    "precio": str(producto.precio_venta),
                    "tipo": producto.get_descripcion_tipo(),
                    "descuento": str(producto.descuento) + str(l.descuento),
                    "es_unico": producto.es_unico
                    }
                )
        else:
            datos.append(
                {
                    "result": True,
                    "codigo_compra": l.codigo_compra,
                    "modelo": l.detalle,
                    "ns_imei": l.ns_imei,
                    "precio": l.p_unidad,
                    "tipo": "Actuacion reparación",
                    "descuento": l.descuento,
                    "es_unico": False
                    }
                )

    return JsonResponse(datos)

@login_required(login_url='login_tk')
def get_modificar_factura(request, id_venta):
    pres = Ventas.objects.filter(pk=id_venta)
    if len(pres) > 0:
        pres = pres[0]
        cliente = pres.cliente
    else:
        cliente = Clientes()

    return render (request, "tienda/ventas/modificar.html",
                   {"c": cliente,
                   "f": pres})

@login_required(login_url='login_tk')
def modificar_factura(request, id_venta):
    if request.method == "POST":
        lineas  = json.loads(request.POST["lineas"])
        venta = Ventas.objects.get(pk=id_venta)
        modificar_lineas_ventas(request, venta)
        if len(lineas) <= 0:
            LineasVentas.objects.filter(venta__pk=venta.pk).delete()
            venta.delete()
        else:
            venta = Ventas.objects.get(pk=id_venta)
            venta.cliente_id = request.POST["cliente_id"]
            venta.forma_pago = request.POST["forma_pago"]
            venta.save()
            for l in lineas:
                try:
                    producto = Productos.objects.get(ns_imei=l["imei"])
                    producto.set_vendido()
                    producto.save()
                    detalle = producto.get_detalle_factura()
                    if producto.es_unico:
                        #guardar historial del producto unico
                        save_historial(request.user.pk, request.POST["cliente_id"],
                                       producto.pk, "Producto vendido")
                except:
                    if "detalle" in l:
                        detalle = l['detalle']
                    else:
                        detalle = ""

                linea = LineasVentas()
                linea.venta_id = venta.id
                linea.ns_imei = l["imei"]
                linea.can = l["can"]
                linea.detalle = detalle
                linea.codigo_compra = l["codigo_compra"]
                linea.descuento = l["descuento"]
                linea.p_unidad = l["total_unidad"]
                linea.save()

    return HttpResponse(reverse("listado_facturas"))


def modificar_lineas_ventas(request, venta):
    lineas = LineasVentas.objects.filter(venta__pk=venta.pk)
    for l in lineas:
        try:
            producto = Productos.objects.get(ns_imei=l.ns_imei)
            producto.estado = 'VT'
            producto.save()
            if producto.es_unico:
                #guardar historial del producto unico
                save_historial(request.user.pk, venta.cliente_id,
                               producto.pk, "Producto modificado en factura o devuelto")
        except:
            pass
        l.delete()

@login_required(login_url='login_tk')
def ch_find_cliente(request):
    if request.method == "POST":
        filter = request.POST["filter"]
        filter_query = Clientes.objects.filter(Q(nombre_completo__contains=filter) |
                                               Q(DNI__contains=filter) |
                                               Q(telefono__contains=filter))
        f_cliente = CPClientesForm()
        return render(request, "tienda/ventas/lista_cliente_ajax.html",
                      {'query': filter_query,
                       'form': f_cliente})
    return redirect("gestion")


@login_required(login_url='login_tk')
def ticket(request):
    request.session["accion_ventas_dni"] = 'ticket'
    return render(request, 'tienda/ventas/ventas.html')



''' Recibe los datos de la factura la guarda en la base de datos,
    crea el documento pdf y lo muestra.  '''
@login_required(login_url='login_tk')
def facturar(request):
    if request.method == "POST":
        venta = Ventas()
        if request.session["accion_ventas_dni"] == "ticket":
            venta.cliente = None
        else:
            venta.cliente_id = request.session["accion_ventas_pk_cliente"]
        venta.empleado_id = request.user.pk
        venta.empleado = request.user.get_full_name()
        venta.forma_pago = request.POST["forma_pago"]
        venta.entrega = request.POST["entrega"]
        venta.save()
        lineas  = json.loads(request.POST["lineas"])
        for l in lineas:
            producto = Productos.objects.get(ns_imei=l["imei"])
            producto.set_vendido()
            producto.save()
            if producto.es_unico:
                #guardar historial del producto unico
                save_historial(request.user.pk, request.session["accion_ventas_pk_cliente"],
                               producto.pk, "Producto vendido")

            linea = LineasVentas()
            linea.venta_id = venta.id
            linea.ns_imei = l["imei"]
            linea.can = l["can"]
            linea.detalle = producto.get_detalle_factura()
            linea.codigo_compra = l["codigo_compra"]
            linea.descuento = l["descuento"]
            linea.p_unidad = l["total_unidad"]
            linea.save()

    vaciar_session_ventas(request)
    return HttpResponse(reverse("get_factura_by_id", args=[venta.pk]))



@login_required(login_url='login_tk')
def facturar_presupuesto(request, id_pres):
    presupuesto = Presupuesto.objects.get(pk=id_pres)
    presupuesto.producto.estado = "CT"
    presupuesto.producto.save()
    if presupuesto.factura != None:
        venta = presupuesto.factura
    else:
        venta = Ventas()
    venta.cliente_id = presupuesto.cliente.pk
    venta.empleado_id = request.user.pk
    venta.empleado = request.user.get_full_name()
    venta.forma_pago = "EF"
    venta.save()
    presupuesto.factura_id = venta.pk
    presupuesto.save()
    lineas  = LineasPresupuesto.objects.filter(presupuesto__pk=presupuesto.pk)
    LineasVentas.objects.filter(venta__pk=venta.pk).delete()
    for l in lineas:
        linea = LineasVentas()
        linea.venta_id = venta.id
        linea.ns_imei = l.codigo
        linea.can = l.can
        linea.detalle = l.detalle
        linea.codigo_compra = l.codigo
        linea.descuento = l.descuento
        linea.p_unidad = l.precio
        linea.save()

    return redirect("get_factura_by_id", id_venta=venta.pk)


# para ver el documento pdf los usuarios
@login_required(login_url='login_tk')
def get_factura_by_id(request, id_venta):
    venta = Ventas.objects.get(pk=id_venta)
    return get_factura(venta)

# para ver el documento pdf los usuarios
@login_required(login_url='login_tk')
def send_factura(request, id_venta):
    venta = Ventas.objects.get(pk=id_venta)
    threading.Thread(target=send_factura_mail, args=(venta,)).start()
    return redirect("listado_facturas")

# para ver el documento pdf los clientes
def get_factura_by_code(request, code):
    datos = json.loads(base64.b64decode(code))
    venta = Ventas.objects.filter(pk=datos["id_venta"])
    return get_factura(venta[0])

# crea el documento pdf y lo muestra
def get_factura(venta):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="factura_%s.pdf"' % venta.id
    docstr = get_documento_venta(venta, venta.cliente, get_first_direccion(venta.cliente))
    response.write(docstr.getvalue())
    return response

@login_required(login_url='login_tk')
def get_all_document(request, id_producto):
    try:
        from pyPdf import PdfFileWriter, PdfFileReader
        from StringIO import StringIO
    except ImportError:
        from io import StringIO
        from PyPDF2 import PdfFileWriter, PdfFileReader

    doc_compra = None
    buffer_doc = StringIO()
    doc_salida = PdfFileWriter()

    producto = Productos.objects.get(pk=id_producto)

    compras = Compras.objects.filter(producto__pk=id_producto)
    if len(compras) > 0:
        compra = compras[0]
        doc_compra = get_documento_compra(producto, compra)
        doc_compra =  PdfFileReader(doc_compra)

    lineas = LineasVentas.objects.filter(ns_imei=producto.ns_imei)
    if len(lineas) > 0:
        venta = lineas[0].venta
        doc_venta = get_documento_venta(venta, venta.cliente, get_first_direccion(venta.cliente))
        doc_venta =  PdfFileReader(doc_venta)
        doc_salida.addPage(doc_venta.getPage(0))
        if doc_compra != None:
            doc_salida.addPage(doc_compra.getPage(0))


        doc_salida.write(buffer_doc)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="docuento_%s.pdf"' % "doc_name"

        response.write(buffer_doc.getvalue())

        return response
    return redirect("informes")


@login_required(login_url='login_tk')
def get_status(request):
    if sepuedeVender(request) :
        return JsonResponse({"result": False})
    elif "accion_ventas_dni" in request.session and request.session["accion_ventas_dni"] == "ticket":
        return JsonResponse({"result": False})
    else:
        return JsonResponse({"result": True})

@login_required(login_url='login_tk')
def salir_venta(request):
    vaciar_session_ventas(request)
    return redirect("tienda")


def send_factura_mail(venta):
    datos = {
        "id_venta": venta.id,
        "id_cliente": venta.cliente.id,
        "email": venta.cliente.email,
    }
    send_data = base64.b64encode(json.dumps(datos))
    url = settings.BASE_URL+ reverse("get_factura_by_code", args=[send_data])
    from django.core.mail import send_mail
    from django.template.loader import render_to_string


    msg_plain = render_to_string(settings.BASE_DIR+'/templates/email/send_factura.html',
                                 {'nombre': venta.cliente.nombre_completo,
                                  "url": url})

    send_mail(
        'Factura de compra',
         msg_plain,
         "info@freakmedia.es",
        [datos['email']],
     )


def vaciar_session_ventas(request):
    if "accion_ventas_dni" in request.session:
        del request.session["accion_ventas_dni"]
    if "accion_ventas_pk_cliente" in request.session:
        del request.session["accion_ventas_pk_cliente"]


def sepuedeVender(request):
    return  "accion_ventas_dni" in request.session and "accion_ventas_pk_cliente" in request.session
