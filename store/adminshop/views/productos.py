# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   29-Sep-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 07-Feb-2018
# @License: Apache license vesion 2.0

from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from adminshop.forms import (ProductosForm, ComplementosForm,
                             EditProductoForm, ModelosForm, EstadoProductosForm)
from adminshop.models import (Modelos, Compras, Presupuesto,
                              Productos, Historial, Testeo)
from adminshop.utility import save_historial, save_doc_firmas
from .compras import guardar_compra
from tokenapi.http import JsonError, JsonResponse

@login_required(login_url='login_tk')
def productos(request, id_producto=-1):
    if not request.method == "POST" and id_producto == -1:
        if "producto_cliente" not in request.session:
            return render(request, "almacen/productos/find_cliente.html",
                          {"mensaje": "Producto nuevo"})

        elif "producto_cliente"  in request.session and "producto_modelo" not in request.session:
            return render(request, "almacen/productos/find_modelos.html")
        else:
            producto = Productos()
            id_modelo = request.session["producto_modelo"]
            producto.modelo_id = id_modelo
            f_productos = ProductosForm(instance=producto)

            return render(request, "almacen/productos/productos.html",
                          {"form": f_productos,
                           "id_modelo": id_modelo,
                           "mensaje": "Producto nuevo"})

    elif not request.method == "POST" and id_producto > 0:
        f_productos = EditProductoForm()
        try:
            producto = Productos.objects.get(pk=id_producto)
            f_productos = EditProductoForm(instance=producto)
        except:
            pass

        return render(request, "almacen/productos/productos.html",
                      {"form": f_productos,
                       "mensaje": "Editar producto",
                       "p": producto})

    elif id_producto > 0:
        try:
            producto = Productos.objects.get(pk=id_producto)
            f_productos = EditProductoForm( request.POST, instance=producto)
            if f_productos.is_valid():
                producto = f_productos.save()

            else:
                print(f_productos.errors)
        except:
            pass
        return redirect("lista_productos")

    else:
        try:
            producto = Productos.objects.get(ns_imei=request.POST.get("ns_imei"))
            f_productos = ProductosForm(request.POST, instance=producto)
        except:
            f_productos = ProductosForm(request.POST)

        if f_productos.is_valid():
            producto = f_productos.save(commit=False)
            producto.modelo_id = request.session["producto_modelo"]
            producto.estado = "ST"
            producto.save()
            compra = guardar_compra(request.session["producto_cliente"], producto.id,
                                    request.user.id, "Compra rapida")

            #Guardamos el documento en la cola para ser firmado
            save_doc_firmas(request.user.pk, compra.pk, "CP")


        if 'producto_modelo' in request.session:
            del request.session["producto_modelo"]
        return redirect("productos")

@login_required(login_url='login_tk')
def complementos(request, id_producto=-1):
    if not request.method == "POST" and id_producto == -1:
        f_productos = ComplementosForm()
        return render(request, "almacen/complementos/editar.html",
                      {"form": f_productos,
                       "categorias": Productos.objects.all(),
                       "titulo": "Producto nuevo"})
    elif not request.method == "POST" and id_producto > 0:
        f_productos = ComplementosForm()
        try:
            producto = Productos.objects.get(pk=id_producto)
            f_productos = ComplementosForm(instance=producto)
        except:
            pass

        return render(request, "almacen/complementos/editar.html",
                      {"form": f_productos,
                       "titulo": "Editar producto",
                       "p": producto})

    elif id_producto > 0:
        try:
            producto = Productos.objects.get(pk=id_producto)
            f_productos = ComplementosForm(request.POST, instance=producto)
            if f_productos.is_valid():
                p = f_productos.save(commit=False)
                p.es_unico = False
                p.estado = "VT"
                p.save()
            else:
                print(f_productos.errors)
        except:
            pass
        return redirect("lista_complementos")

    else:
        f_productos = ComplementosForm(request.POST)
        if f_productos.is_valid():
            p = f_productos.save(commit=False)
            p.es_unico = False
            p.estado = "VT"
            p.save()
        else:
            print(f_productos.errors)
        return redirect("lista_complementos")

@login_required(login_url='login_tk')
def save_complemento(request):
    if request.method == "POST":
        try:
            producto = Productos.objects.get(ns_imei=request.POST.get("ns_imei"))
        except:
            producto = Productos()

        producto.ns_imei=request.POST["ns_imei"]
        producto.detalle=request.POST["detalle"]
        producto.precio_venta=request.POST["precio_venta"].replace(",",".")
        producto.es_unico=False
        producto.estado="VT"
        producto.save()

        compra = Compras(codigo_compra=request.POST["codigo_compra"],
                         producto_id=producto.id,
                         usuario_id=request.user.id)
        compra.save()
        datos = {
            "result": True,
            "codigo_compra": compra.codigo_compra,
            "modelo": unicode(producto),
            "ns_imei": producto.ns_imei,
            "precio": str(producto.precio_venta),
            "tipo": producto.get_descripcion_tipo(),
            "descuento": str(producto.descuento),
            "es_unico": producto.es_unico
        }
        return JsonResponse(datos)
    return JsonError("Solo puede ser peticiones POST")



@login_required(login_url='login_tk')
def salir_productos_usados(request):
    if 'producto_cliente' in request.session:
        del request.session["producto_cliente"]
    return redirect("almacen")

@login_required(login_url='login_tk')
def modificar_precio_venta(request, id_producto):
    if request.method == "POST":
        producto = Productos.objects.get(pk=id_producto)
        producto.estado = "VT"
        producto.precio_venta = request.POST["precio_venta"]
        producto.save()
        return JsonResponse({'precio':producto.precio_venta})
    else:
        return JsonError("solo peticiones post")


@login_required(login_url='login_tk')
def salir_elegir_modelo(request):
    if 'producto_cliente' in request.session:
        del request.session["producto_cliente"]
    return redirect("productos")

@login_required(login_url='login_tk')
def al_set_cliente(request, id_cliente):
    request.session["producto_cliente"] = id_cliente
    return redirect("productos")

@login_required(login_url='login_tk')
def al_set_modelo(request, id_modelo):
    request.session["producto_modelo"] = id_modelo
    return redirect("productos")


@login_required(login_url='login_tk')
def lista_complementos(request):
    if request.method == "POST":
        filter = request.POST["filter"]
        filter_query = Productos.objects.filter(Q(ns_imei__icontains=filter) |
                                               Q(detalle__icontains=filter)).exclude(Q(es_unico=True))
        return render(request, "almacen/complementos/listado.html", {'query': filter_query})
    else:
        filter_query = Productos.objects.all().exclude(Q(es_unico=True))
        return render(request, "almacen/complementos/listado.html", {'query': filter_query})

@login_required(login_url='login_tk')
def rm_producto(request, id_producto, pg="lista_complementos"):
    try:
        Productos.objects.get(pk=id_producto).delete()
    except:
        pass

    return redirect(pg)


@login_required(login_url='login_tk')
def lista_productos(request, estado):
    if request.method == "POST":
        filter_query = []
        if 'filter' in request.POST:
            filter = request.POST["filter"]
            if len(filter) > 0 and estado in ["OK", "PD", "PS", "RP"] and filter[0].upper() == "P":
                filter = filter.replace("P", "")
                filter = filter.replace("p", "")
                imei = 0
                ps = Presupuesto.objects.filter(pk=filter)
                if len(ps) > 0:
                    imei = ps[0].producto.ns_imei
                filter_query = Productos.objects.filter(Q(ns_imei__icontains=imei))
            elif len(filter) > 0 and estado in ["OK", "PD", "PS", "RP"] and filter[0].upper() == "C":
                filter = filter[1:]
                imei = 0
                ps = Presupuesto.objects.filter(cliente__DNI__icontains=filter)
                if len(ps) > 0:
                    imei = ps[0].producto.ns_imei
                filter_query = Productos.objects.filter(Q(ns_imei__icontains=imei))
            elif estado == "all" and  request.POST["filter"] != "":
                filter_query = Productos.objects.filter(Q(ns_imei__icontains=filter))
            else:
                filter_query = Productos.objects.filter(Q(ns_imei__icontains=filter) &
                                                        Q(estado=estado)).exclude(es_unico=False)
        if estado in ["VT", "ST"]:
            ch = "disponibles"
        elif estado in ["OK", "PD", "RP", "PS"]:
            ch = "taller"
        else:
            ch = ""

        return render(request, "almacen/productos/lista_productos_ajax.html",
                      {'query': filter_query,
                       "estado": estado,
                       "form_estado": EstadoProductosForm(),
                       "ch": ch})
    else:
        if estado in ["VT", "ST"]:
            ch = "disponibles"
        elif estado in ["OK", "PD", "RP", "PS"]:
            ch = "taller"
        else:
            ch = None

        filter_query = Productos.objects.filter(Q(estado=estado)).exclude(es_unico=False)
        return render(request, "almacen/productos/lista_productos.html",
                      {'query': filter_query,
                       "estado": estado,
                       "form_estado": EstadoProductosForm(),
                       "ch":ch})

@login_required(login_url='login_tk')
def cambiar_estado(request, id):
    if request.method == "POST":
        producto = Productos.objects.get(pk=id)
        form = EstadoProductosForm(request.POST, instance=producto)
        producto = form.save()
        filter_query = Productos.objects.filter(pk=id)
        estado = producto.estado
        h = Historial.objects.filter(producto__id=id)[0]

        save_historial(request.user.pk, h.cliente_id,
                       producto.pk, "Cambio de estado del producto.")

        if estado in ["VT", "ST"]:
            ch = "disponibles"
        elif estado in ["OK", "PD", "RP"]:
            ch = "taller"
        else:
            ch = None

        return render(request, "almacen/productos/lista_productos.html",
                      {'query': filter_query,
                       "estado": 'all',
                       "form_estado": EstadoProductosForm(),
                       "ch":ch})
    else:
        return redirect("tienda")




@login_required(login_url='login_tk')
def get_historial(request, id_producto):
    producto = Productos.objects.get(pk=id_producto)
    filter_query = Historial.objects.filter(producto__id=id_producto)
    return render(request, "almacen/historial.html",
                  {'query': filter_query, "p": producto,
                   "recuperar": producto.estado == "CT"})
