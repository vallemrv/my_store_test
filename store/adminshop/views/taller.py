# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   29-Sep-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 17-Dec-2017
# @License: Apache license vesion 2.0

from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from adminshop.forms import (TipoTesteoForm, FinTesteoForm, ActuacionesForm, NotasReparacionForm)
from adminshop.models import (Productos, ListaTesteo, Testeo, Presupuesto, Clientes,
                              Historial, Reparaciones, NotasReparacion,
                              ESTADO_CHOICES_TESTEO)
from adminshop.utility import save_historial
from tokenapi.http import JsonError, JsonResponse
import threading

def send_men_rep(cliente, estado):
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    if estado=="OK":
        mens = "terminal_reparado"
        asunto = "Terminal reparado"
    else:
        mens = "terminal_no_reparado"
        asunto = "Reparacion no viable"
    msg_plain = render_to_string(settings.BASE_DIR+'/templates/email/%s.html' % mens,
                                 {'nombre': cliente.nombre_completo})

    send_mail(
         asunto,
         msg_plain,
         "info@freakmedia.es",
        [cliente.email],
     )


@login_required(login_url='login_tk')
def add_nota_reparacion(request, id_pres):
    if request.method == "POST":
        f_notas = NotasReparacionForm(request.POST)
        if f_notas.is_valid():
            notas = f_notas.save(commit=False)
            notas.usuario_id = request.user.pk
            notas.presupuesto_id = id_pres
            presupuesto = Presupuesto.objects.get(pk=id_pres)
            notas.save()

    return redirect("reparacion", id_producto=presupuesto.producto.pk)

@login_required(login_url='login_tk')
def rm_nota_reparacion(request, id_nota, id_producto):
    try:
        NotasReparacion.objects.filter(pk=id_nota).delete()
    except Exception as e:
        pass

    return redirect("reparacion", id_producto=id_producto)


@login_required(login_url='login_tk')
def actuaciones(request, id_actuacion=-1):
    if not request.method == "POST" and id_actuacion == -1:
        f_actuacion = ActuacionesForm()
        return render(request, "taller/actuaciones.html",
                      {"form": f_actuacion,
                       "actuaciones": Reparaciones.objects.all(),
                       "mensaje": "Actuacion nueva"})
    elif not request.method == "POST" and id_actuacion > 0:
        f_actuacion = ActuacionesForm()
        try:
            actuacion = Reparaciones.objects.get(pk=id_actuacion)
            f_actuacion = ActuacionesForm(instance=actuacion)
        except:
            pass


        return render(request, "taller/actuaciones.html",
                      {"form": f_actuacion,
                       "actuaciones": Reparaciones.objects.all(),
                       "mensaje": "Editar actuacion"})

    elif id_actuacion > 0:
        try:
            actuacion = Reparaciones.objects.get(pk=id_actuacion)
            f_actuacion = ActuacionesForm( request.POST, instance=actuacion)
            if f_actuacion.is_valid():
                f_actuacion.save()
                f_actuacion = ActuacionesForm()
        except:
            pass
        return redirect("actuaciones")

    else:
        f_actuacion = ActuacionesForm(request.POST)
        if f_actuacion.is_valid():
            f_actuacion.save()
            f_actuacion = ActuacionesForm()
        return render(request, "taller/actuaciones.html",
                      {"form": f_actuacion,
                       "actuaciones": Reparaciones.objects.all(),
                       "mensaje": "Actuacion nueva"})

@login_required(login_url='login_tk')
def rm_actuacion(request, id_actuacion):
    try:
        Reparaciones.objects.get(pk=id_actuacion).delete()
    except:
        pass

    return redirect("actuaciones")

@login_required(login_url='login_tk')
def find_actuacion_taller(request):
    codigo = request.POST['codigo']
    datos = Reparaciones.objects.filter(Q(detalle__contains=codigo) |
                                        Q(codigo__contains=codigo))
    f_actuacion = ActuacionesForm()
    return render(request, "taller/actuaciones.html",
                  {"form": f_actuacion,
                   "actuaciones": datos})

@login_required(login_url='login_tk')
def set_reparado(request, id_producto, estado='OK'):
    pres = Presupuesto.objects.filter(producto__pk=id_producto)
    if len(pres) > 0:
        pres = pres[0]
        cliente = pres.cliente
    producto = Productos.objects.get(pk=id_producto)
    producto.estado = "OK"
    producto.save()
    #Guardamos el historial de la accion
    save_historial(request.user.pk, cliente.pk,
                    id_producto, "Producto reparado...")


    threading.Thread(target=send_men_rep, args=(cliente, estado,)).start()
    return redirect("lista_productos", estado='RP')

@login_required(login_url='login_tk')
def reparacion(request, id_producto):
    try:
        pres = Presupuesto.objects.filter(producto__pk=id_producto)
        cliente = Clientes()
        if len(pres) > 0:
            pres = pres[0]
            cliente = pres.cliente
    except:
        pres = Presupuesto()

    form_notas = NotasReparacionForm()
    return render (request, "taller/hoja_reparacion.html",
                   {"c": cliente,
                    "p": pres,
                    "notas": NotasReparacion.objects.filter(presupuesto_id=pres.pk),
                    "form_notas":  form_notas})

@login_required(login_url='login_tk')
def save_actuacion(request):
    if request.method == "POST":
        try:
            actuacion = Reparaciones.objects.get(codigo=request.POST.get("codigo"))
        except:
            actuacion = Reparaciones()

        actuacion.codigo=request.POST["codigo"]
        actuacion.detalle=request.POST["detalle"]
        actuacion.precio=request.POST["precio"].replace(",",".")

        actuacion.save()

        datos = {
            "result": True,
            "pk": actuacion.pk,
            "codigo": actuacion.codigo,
            "can": 1,
            "descuento": 0,
            "detalle": actuacion.detalle,
            "precio": actuacion.precio,
        }
        return JsonResponse(datos)
    return JsonError("Solo puede ser peticiones POST")


@login_required(login_url='login_tk')
def tipo_testeo(request, id_tipo=-1):
    if not request.method == "POST" and id_tipo == -1:
        f_tipo = TipoTesteoForm()
        return render(request, "taller/tipo_testeo.html",
                      {"form": f_tipo,
                       "tipos": ListaTesteo.objects.all(),
                       "mensaje": "Tipo nuevo"})
    elif not request.method == "POST" and id_tipo > 0:
        f_tipo = TipoTesteoForm()
        try:
            catergoria = ListaTesteo.objects.get(pk=id_tipo)
            f_tipo = TipoTesteoForm(instance=catergoria)
        except:
            pass


        return render(request, "taller/tipo_testeo.html",
                      {"form": f_tipo,
                       "tipos": ListaTesteo.objects.all(),
                       "mensaje": "Editar tipo"})

    elif id_tipo > 0:
        try:
            catergoria = ListaTesteo.objects.get(pk=id_tipo)
            f_tipo = TipoTesteoForm( request.POST, instance=catergoria)
            if f_tipo.is_valid():
                f_tipo.save()
        except:
            pass
        return redirect("tipo_testeo")

    else:
        f_tipo = TipoTesteoForm(request.POST)
        if f_tipo.is_valid():
            f_tipo.save()
        return redirect("tipo_testeo")

@login_required(login_url='login_tk')
def rm_tipo_testeo(request, id_tipo):
    try:
        ListaTesteo.objects.get(pk=id_tipo).delete()
    except:
        pass

    return redirect("tipo_testeo")


@login_required(login_url='login_tk')
def testeo(request, id_producto):
    producto = Productos.objects.get(pk=id_producto)

    return render(request, "taller/testeo.html",{
        "p": producto,
        "ListaTesteo": ListaTesteo.objects.filter(categoria=producto.modelo.categoria),
        "estado_test": ESTADO_CHOICES_TESTEO,
        "form": FinTesteoForm(instance=producto)
    })


@login_required(login_url='login_tk')
def set_estado_testeo(request, test_id, p_id, estado):
    testeos = Testeo.objects.filter(Q(descripcion__pk=test_id) &
                                     Q(producto__pk=p_id))
    if len(testeos) > 0:
        test = testeos[0]
    else:
        test = Testeo()

    test.producto_id = p_id
    test.estado = estado
    test.descripcion_id = test_id
    test.save()
    return HttpResponse("success")


@login_required(login_url='login_tk')
def finalizar_testeo(request):
    if request.method == "POST":
        p_id = request.POST["p_id"]
        producto = Productos.objects.get(pk=p_id)
        f_p = FinTesteoForm(request.POST, instance=producto)
        if f_p.is_valid():
            p = f_p.save()
            p.estado = "TD"
            p.save()
            h = Historial()
            clientes = Historial.objects.filter(producto_id=p.pk)
            cliente_id = 1
            if len(clientes) > 0:
                cliente_id = clientes[0].cliente_id
            h.producto_id = p.id
            h.usuario_id = request.user.id
            h.cliente_id = cliente_id
            h.detalle =  "Finalización del testeo y valoración del producto"
            h.save()
            return redirect("lista_productos", estado="OS")


@login_required(login_url='login_tk')
def volver_testear_producto(request, id_producto):
    p = Productos.objects.get(pk=id_producto)
    p.estado = "OS"
    p.save()
    return redirect("tienda")
