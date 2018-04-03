# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   03-Dec-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 19-Jan-2018
# @License: Apache license vesion 2.0

from django.db.models import Q
from django.forms.models import model_to_dict
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from adminshop.forms import  (DireccionesForm, ModelosForm, ProductosForm,
                              ProveedoresForm,  CPProductosForm, ProveedorCompra)
from adminshop.models import  (Clientes, Direcciones, Proveedores,
                               Productos, Modelos, Tipos, Compras)
from adminshop.utility import save_historial, save_doc_firmas, save_doc_testeo

@login_required(login_url='login_tk')
def proveedores(request, id_proveedor=-1):
    if not request.method == "POST" and id_proveedor == -1:
        f_proveedor = ProveedoresForm()
        return render(request, 'gestion/proveedores/proveedores.html',
                      {"form": f_proveedor,
                       "titulo": "Proveedor nuevo" })

    elif not request.method == "POST" and id_proveedor > 0:
        f_proveedor = ProveedoresForm()
        try:
            proveedor = Proveedores.objects.get(pk=id_proveedor)
            f_proveedor = ProveedoresForm(instance=proveedor)
        except:
            pass
        return render(request, 'gestion/proveedores/proveedores.html',
                      {"form": f_proveedor,
                       "titulo": "Editar proveedor" })
    elif id_proveedor > 0:
        f_proveedor = ProveedoresForm()
        try:
            proveedor = Proveedores.objects.get(pk=id_proveedor)
            f_proveedor = ProveedoresForm(instance=proveedor)
        except:
            pass

        if f_proveedor.is_valid():
            proveedor = f_proveedor.save()
        return redirect("lista_proveedores")
    else:
        f_proveedor = ProveedoresForm(request.POST)
        if f_proveedor.is_valid():
            proveedor = f_proveedor.save()
        return redirect("lista_proveedores")

@login_required(login_url='login_tk')
def rm_proveedores(request, id_proveedor):
    try:
        for p in Proveedores.objects.get(pk=id_proveedor):
            p.activo = False
            p.save()
    except:
        pass

    return redirect("lista_proveedores")


@login_required(login_url='login_tk')
def lista_proveedores(request):
    if request.method == "POST":
        filter = request.POST["filter"]
        filter_query = Proveedores.objects.filter(Q(CIF__contains=filter) |
                                                  Q(razon_social__contains=filter) |
                                                  Q(telefono__contains=filter)).exclude(activo=False)
        return render(request, "gestion/proveedores/lista_proveedores.html", {'query': filter_query})
    else:
        filter_query = Proveedores.objects.all().exclude(activo=False)
        return render(request, "gestion/proveedores/lista_proveedores.html", {'query': filter_query})


@login_required(login_url='login_tk')
def find_proveedor(request):
    if request.method == "POST" and "CIF" in request.POST:
        return cp_proveedor(request)

    return render(request, 'proveedor/find_proveedor.html')


@login_required(login_url='login_tk')
def cp_proveedor(request):
    if request.method == 'POST':
        if len(request.POST) == 2 and "CIF" in request.POST:
            proveedores = Proveedores.objects.filter(CIF__contains=request.POST.get('CIF'))
            if len(proveedores) > 0:
                form = ProveedoresForm (instance=proveedores[0])
                titulo = 'Proveedor existente'
                tipo = "comprar"
                request.session["accion_comprar_cif"] = request.POST.get('CIF')
                request.session["accion_comprar_pk_proveedor"] = proveedores[0].pk
            else:
                form = ProveedoresForm(request.POST)
                titulo = 'Proveedor no existe'
                tipo = "no_existe"
            return render(request, 'proveedor/proveedores.html',
                    {'form':form, 'titulo': titulo,
                     'tipo': tipo})


        if len(request.POST) > 2:
            tipo = "comprar"
            proveedores = Proveedores.objects.filter(CIF__contains=request.POST.get('CIF'))
            request.session["accion_comprar_cif"] = request.POST.get('CIF')
            if len(proveedores) > 0:
                form = ProveedoresForm(request.POST, instance=proveedores[0])
            else:
                form = ProveedoresForm(request.POST)

            if form.is_valid():
                proveedor = form.save()
            else:
                return render(request, 'proveedor/proveedores.html',
                        {'form':form, 'titulo': "Error al guardar el proveedor",
                         'tipo': tipo, "form_error": form.errors})

            request.session["accion_comprar_pk_proveedor"] = proveedor.pk
            return render(request, 'proveedor/proveedores.html',
                    {'form':form, 'titulo': "Proveedor guardado o modificado",
                     'tipo': tipo})

    return redirect("find_proveedor")

@login_required(login_url='login_tk')
def salir_compra_proveedor(request):
    vaciar_sesison_compra_proveedor(request)
    return redirect("almacen")

@login_required(login_url='login_tk')
def cp_productos_proveedor(request, id_modelo=-1):
    if "accion_comprar_cif" in request.session:
        if request.method != "POST" and id_modelo < 0:
            f_modelo = ModelosForm()
            return render(request, 'proveedor/find_modelos.html',
                          {"form": f_modelo})
        elif request.method != "POST" and id_modelo > 0:
            request.session["accion_comprar_pro_pk_modelo"] = id_modelo
            try:
                modelo = Modelos.objects.get(pk=id_modelo)
            except:
                modelo = Modelos()
            tipo = "no_existe"
            producto = Productos()
            producto.modelo_id = modelo.pk
            producto.precio_compra = modelo.precio_usado
            tipos = Tipos.objects.all()
            #producto.tipo_id = tipos[0].pk if len(tipos) > 0 else -1
            form = ProductosForm(instance=producto)
            return render(request, 'proveedor/productos.html',
                          {'form':form, 'titulo': "Datos del producto",
                           'modelo': modelo,
                           'tipo': tipo})
        else:
            try:
                producto = Productos.objects.get(ns_imei=request.POST.get("ns_imei"))
                form = ProductosForm(request.POST, instance=producto)
            except Exception as p:
                form = ProductosForm(request.POST)

            producto_str = ""
            if form.is_valid():
                producto = form.save(commit=False)
                if "accion_comprar_pro_pk_modelo" not in request.session:
                    vaciar_sesison_compra_proveedor(request)
                    return redirect("tienda")
                producto.modelo_id = request.session["accion_comprar_pro_pk_modelo"]
                producto.estado = "ST"
                producto.save()
                request.session["accion_comprar_pro_pk_producto"] = producto.pk
                save_historial(request.user.pk, request.session["accion_comprar_pk_proveedor"],
                               request.session["accion_comprar_pro_pk_producto"],
                               "Producto comprado a un proveedor")


                producto_str = Productos.objects.get(pk=producto.pk).modelo.nombre
                form = ProveedorCompra()

            return render(request, 'proveedor/compras.html',
                          {'form':form, 'titulo': "Datos del producto",
                           "form_error": form.errors,
                           "producto_str": producto_str,
                           "id_modelo":  request.session["accion_comprar_pro_pk_modelo"]})


    else:
        return redirect("tienda")


@login_required(login_url='login_tk')
def finalizar_compra_proveedor(request):
    if  request.method == "POST":
        f_config = ProveedorCompra(request.POST, request.FILES)
        if f_config.is_valid():
            compra = f_config.save(commit=False)
            compra.producto_id = request.session["accion_comprar_pro_pk_producto"]
            compra.vendedor_id = request.session["accion_comprar_pk_proveedor"]
            compra.usuario_id = request.user.id
            compra.tipo_vendedor = "PV"
            compra.save()

            vaciar_sesison_compra_proveedor(request, todo=False)
            return redirect("cp_productos_proveedor_none")
        else:
            print(f_config.errors)



@login_required(login_url='login_tk')
def cp_lista_modelos_proveedor(request):
    if request.method == "POST":
        filter = request.POST["filter"]
        filter_query = Modelos.objects.filter(Q(nombre__contains=filter))
        return render(request, "proveedor/lista_modelos.html", {'query': filter_query})


def vaciar_sesison_compra_proveedor(request, todo=True):
    if todo and "accion_comprar_pk_proveedor" in request.session:
        del request.session["accion_comprar_pk_proveedor"]
    if "accion_comprar_pro_pk_producto" in request.session:
        del request.session["accion_comprar_pro_pk_producto"]
    if "accion_comprar_pro_pk_modelo" in request.session:
        del request.session["accion_comprar_pro_pk_modelo"]
    if todo and "accion_comprar_cif" in request.session:
        del request.session["accion_comprar_cif"]
