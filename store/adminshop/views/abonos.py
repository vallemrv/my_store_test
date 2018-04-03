# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   30-Nov-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 08-Feb-2018
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
from adminshop.utility import get_documento_abono
from . import get_first_direccion
from adminshop.forms import (CPClientesForm)
from adminshop.models import (Abonos, LineasAbonos, Clientes, Productos, Ventas,
                              LineasVentas, Historial, Direcciones)
from django.template.loader import get_template
#from django.template import Context
from . import validoDNI, get_first_direccion, set_first_direccion
from tokenapi.http import JsonResponse, JsonError
from datetime import datetime
import threading
import base64
import json
import trml2pdf
import os

# Create your views here.
@login_required(login_url='login_tk')
def abonos_find_cliente(request):
    vaciar_session_abonos(request)
    if request.method == "POST" and "DNI" in request.POST:
        if validoDNI(request.POST["DNI"]):
            return abonos_clientes(request)
        else:
            return render(request, 'tienda/compras/find_cliente.html',{
                "mensaje": "DNI no valido"
            })

    return render(request, 'tienda/compras/find_cliente.html')


@login_required(login_url='login_tk')
def abonos_clientes(request):
    if request.method == 'POST':
        if len(request.POST) == 2 and "DNI" in request.POST:
            clientes = Clientes.objects.filter(DNI__icontains=request.POST.get('DNI'))
            if len(clientes) > 0:
                direccion = get_first_direccion(clientes[0].id)
                full_data = dict(model_to_dict(direccion).items() + model_to_dict(clientes[0]).items())
                form = CPClientesForm (full_data, instance=clientes[0])
                titulo = 'Cliente existente'
                tipo = "abonar"
                request.session["accion_abonos_dni"] = request.POST.get('DNI')
                request.session["accion_abonos_pk_cliente"] = clientes[0].pk
            else:
                form = CPClientesForm(request.POST)
                titulo = 'Cliente no existe'
                tipo = "no_existe"
            return render(request, 'tienda/compras/clientes.html',
                    {'form':form, 'titulo': titulo, 'tipo': tipo} )


        if len(request.POST) > 2:
            clientes = Clientes.objects.filter(DNI__icontains=request.POST.get('DNI'))
            request.session["accion_abonos_dni"] = request.POST.get('DNI')
            tipo = "abonar"
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

            request.session["accion_abonos_pk_cliente"] = cliente.pk
            return render(request, 'tienda/compras/clientes.html',
                    {'form':form, 'titulo': "Cliente guardado o modificado",
                     'tipo': tipo})

    return redirect("find_cliente")

@login_required(login_url='login_tk')
def salir_abonar(request):
    vaciar_session_abonos(request)
    return redirect("tienda")

'''
    Si el cliente esta activo muestra vista de abonos
    si no la busqueda del cliente
'''
@login_required(login_url='login_tk')
def abonos(request):
    if "accion_abonos_dni" in request.session:
        return render(request, 'tienda/abonos/factura.html')
    else:
        return redirect("abonos_find_cliente")


''' Recibe los datos de la factura la guarda en la base de datos,
    crea el documento pdf y lo muestra.  '''
@login_required(login_url='login_tk')
def abonar(request):
    if request.method == "POST":
        abono = Abonos()
        abono.cliente_id = request.session["accion_abonos_pk_cliente"]
        abono.empleado_id = request.user.pk
        abono.empleado = request.user.get_full_name()
        abono.forma_pago = request.POST["forma_pago"]
        abono.factura_id = request.POST["factura_id"]
        abono.save()
        lineas  = json.loads(request.POST["lineas"])
        for l in lineas:
            producto = Productos.objects.get(ns_imei=l["imei"])
            producto.estado = "VT"
            producto.save()
            if producto.es_unico:
                historial = Historial()
                historial.cliente_id = request.session["accion_abonos_pk_cliente"]
                historial.producto_id = producto.pk
                historial.usuario_id = request.user.pk
                historial.detalle = "Producto abonoado o devuelto"
                historial.save()
            linea = LineasAbonos()
            linea.abono_id = abono.id
            linea.ns_imei = l["imei"]
            linea.can = l["can"]
            linea.descuento = l["descuento"].replace(",", ".")
            linea.detalle = producto.get_detalle_factura()
            linea.codigo_compra = l["codigo_compra"]
            linea.p_unidad = l["total_unidad"].replace(",", ".")
            linea.save()

    vaciar_session_abonos(request)
    return HttpResponse(reverse("get_abono_by_id", args=[abono.pk]))

@login_required(login_url='login_tk')
def listado_abonos(request):
    facturas  = Abonos.objects.all()
    return render(request, 'tienda/abonos/listado.html',{
        "facturas": facturas
    })

@login_required(login_url='login_tk')
def find_abonos(request):
    filter = request.POST["filter"]
    if filter[0].upper() == "A":
        filter = filter.replace("A", "")
        filter = filter.replace("a", "")
        facturas  = Abonos.objects.filter(Q(pk=filter))
    else:
        facturas  = Abonos.objects.filter(Q(fecha_salida__icontains=filter)|
                                          Q(cliente__DNI__icontains=filter)|
                                          Q(cliente__nombre_completo__icontains=filter))
    return render(request, 'tienda/abonos/listado_ajax.html',{
        "facturas": facturas
    })


# para ver el documento pdf los usuarios
@login_required(login_url='login_tk')
def get_abono_by_id(request, id_abono):
    abono = Abonos.objects.get(pk=id_abono)
    return get_abono(abono)


# crea el documento pdf y lo muestra
def get_abono(abono):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="abono_%s.pdf"' % abono.id
    docstr = get_documento_abono(abono, abono.cliente, get_first_direccion(abono.cliente))
    response.write(docstr.getvalue())
    return response



@login_required(login_url='login_tk')
def get_productos_factura(request):
    ventas_id = request.POST['ventas_id']
    cliente_id = request.session["accion_abonos_pk_cliente"]
    datos = {}
    lineas = []
    lineas_ventas = LineasVentas.objects.filter(Q(venta__pk=ventas_id) &
                                                Q(venta__cliente_id=cliente_id))

    for l in lineas_ventas:
        abonos = LineasAbonos.objects.filter(Q(ns_imei=l.ns_imei) &
                                             Q(abono__factura_id=ventas_id))
        if len(abonos) <= 0:
            lineas.append(l)

    return render(request, "tienda/abonos/lineasventas.html",
                 {"lineas": lineas})


@login_required(login_url='login_tk')
def get_producto_abonar(request):
    ns_imei = request.POST['ns_imei']
    cliente_id = request.session["accion_abonos_pk_cliente"]
    datos = {}
    try:
        producto = Productos.objects.get(ns_imei=ns_imei)
    except:
        return JsonError("No se ha encontrado coincidencias")

    linea = LineasVentas.objects.filter(Q(ns_imei=ns_imei) &
                                        Q(venta__cliente_id=cliente_id))[0]

    datos = {
        "result": True,
        "codigo_compra": linea.codigo_compra,
        "modelo": unicode(producto),
        "ns_imei": producto.ns_imei,
        "precio": linea.p_unidad,
        "descuento": linea.descuento,
        "tipo": producto.get_descripcion_tipo(),
        "es_unico": producto.es_unico
    }

    return JsonResponse(datos)

# para ver el documento pdf los usuarios
@login_required(login_url='login_tk')
def send_abono(request, id_abono):
    abono = Ventas.objects.get(pk=id_abono)
    threading.Thread(target=send_abono_mail, args=(abono,)).start()
    return redirect("listado_abonos")


@login_required(login_url='login_tk')
def get_status_abonos(request):
    if not sepuedeAbonar(request):
        return JsonResponse({"result": True})
    else:
        return JsonResponse({"result": False})

# para ver el documento pdf los clientes
def get_abono_by_code(request, code):
    datos = json.loads(base64.b64decode(code))
    abonos = Abonos.objects.filter(pk=datos["id_abono"])
    return get_abono(abonos[0])


def send_abono_mail(abono):
    datos = {
        "id_abono": abono.id,
        "id_cliente": abono.cliente.id,
        "email": abono.cliente.email,
    }
    send_data = base64.b64encode(json.dumps(datos))
    url = settings.BASE_URL+ reverse("get_abono_by_code", args=[send_data])
    from django.core.mail import send_mail
    from django.template.loader import render_to_string


    msg_plain = render_to_string(settings.BASE_DIR+'/templates/email/send_abono.html',
                                 {'nombre': abono.cliente.nombre_completo,
                                  "url": url})

    send_mail(
        'Abono de compra',
         msg_plain,
         "info@freakmedia.es",
        [datos['email']],
     )



def vaciar_session_abonos(request):
    if "accion_abonos_dni" in request.session:
        del request.session["accion_abonos_dni"]
    if "accion_abonos_pk_cliente" in request.session:
        del request.session["accion_abonos_pk_cliente"]


def sepuedeAbonar(request):
    return  "accion_abonos_dni" in request.session and "accion_abonos_pk_cliente" in request.session
