# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   28-Sep-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 04-Dec-2017
# @License: Apache license vesion 2.0

from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from adminshop.forms import CategoriasForm,  ProductosForm, MarcasForm, ModelosForm
from adminshop.models import Categorias, Marcas, Modelos, Productos

@login_required(login_url='login_tk')
def categorias(request, id_categoria=-1):
    if not request.method == "POST" and id_categoria == -1:
        f_categoria = CategoriasForm()
        return render(request, "gestion/categorias.html",
                      {"form": f_categoria,
                       "categorias": Categorias.objects.all(),
                       "mensaje": "Categoria nueva"})
    elif not request.method == "POST" and id_categoria > 0:
        f_categoria = CategoriasForm()
        try:
            catergoria = Categorias.objects.get(pk=id_categoria)
            f_categoria = CategoriasForm(instance=catergoria)
        except:
            pass


        return render(request, "gestion/categorias.html",
                      {"form": f_categoria,
                       "categorias": Categorias.objects.all(),
                       "mensaje": "Editar categoria"})

    elif id_categoria > 0:
        try:
            catergoria = Categorias.objects.get(pk=id_categoria)
            f_categoria = CategoriasForm( request.POST, instance=catergoria)
            if f_categoria.is_valid():
                f_categoria.save()
                f_categoria = CategoriasForm()
        except:
            pass
        return redirect("categorias")

    else:
        f_categoria = CategoriasForm(request.POST)
        if f_categoria.is_valid():
            f_categoria.save()
            f_categoria = CategoriasForm()
        return render(request, "gestion/categorias.html",
                      {"form": f_categoria,
                       "categorias": Categorias.objects.all(),
                       "mensaje": "Categoria nueva"})

@login_required(login_url='login_tk')
def rm_categorias(request, id_categoria):
    try:
        Categorias.objects.get(pk=id_categoria).delete()
    except:
        pass

    return redirect("categorias")

@login_required(login_url='login_tk')
def marcas(request, id_marca=-1):
    if not request.method == "POST" and id_marca == -1:
        f_marca = MarcasForm()
        return render(request, "gestion/marcas.html",
                      {"form": f_marca,
                       "marcas": Marcas.objects.all(),
                       "mensaje": "Marca nueva"})
    elif not request.method == "POST" and id_marca > 0:
        f_marca = MarcasForm()
        try:
            marca = Marcas.objects.get(pk=id_marca)
            f_marca = MarcasForm(instance=marca)
        except:
            pass


        return render(request, "gestion/marcas.html",
                      {"form": f_marca,
                       "macas": Marcas.objects.all(),
                       "mensaje": "Editar marca"})

    elif id_marca > 0:
        try:
            marca = Marcas.objects.get(pk=id_marca)
            f_marca = MarcasForm(request.POST, request.FILES, instance=marca)
            if f_marca.is_valid():
                f_marca.save()
        except:
            pass
        return redirect("marcas")

    else:
        f_marca = MarcasForm(request.POST, request.FILES)
        if f_marca.is_valid():
            f_marca.save()
        return redirect("marcas")

@login_required(login_url='login_tk')
def rm_marcas(request, id_marca):
    try:
        Marcas.objects.get(pk=id_marca).delete()
    except:
        pass

    return redirect("marcas")

@login_required(login_url='login_tk')
def al_find_modelo(request):
    if request.method == "POST":
        filter = request.POST["filter"]
        filter_query = Modelos.objects.filter(Q(nombre__contains=filter) |
                                              Q(marca__nombre__contains=filter))
        f_modelo = ModelosForm()
        return render(request, "gestion/lista_modelos.html",
                      {'query': filter_query,
                       'form': f_modelo })


@login_required(login_url='login_tk')
def lista_modelos(request):
    if request.method == "POST":
        filter = request.POST["filter"]
        filter_query = Modelos.objects.filter(Q(nombre__contains=filter) |
                                              Q(marca__nombre__contains=filter))
        return render(request, "gestion/lista_modelos_ajax.html",
                      {'modelos': filter_query,})


@login_required(login_url='login_tk')
def save_modelo(request):
    from tokenapi.http import JsonResponse, JsonError
    f_modelo = ModelosForm(request.POST)
    if f_modelo.is_valid():
        modelo = f_modelo.save()
        return JsonResponse({'id': modelo.id})
    else:
        return JsonError("formulario no valido")

@login_required(login_url='login_tk')
def modelos(request, id_modelo=-1):
    if not request.method == "POST" and id_modelo == -1:
        f_modelo = ModelosForm()
        return render(request, "gestion/modelos.html",
                      {"form": f_modelo,
                       "modelos": Modelos.objects.all(),
                       "mensaje": "Modelo nuevo"})
    elif not request.method == "POST" and id_modelo > 0:
        f_modelo = ModelosForm()
        try:
            modelo = Modelos.objects.get(pk=id_modelo)
            f_modelo = ModelosForm(instance=modelo)
        except:
            pass


        return render(request, "gestion/modelos.html",
                      {"form": f_modelo,
                       "modelos": Modelos.objects.all(),
                       "mensaje": "Editar modelo"})

    elif id_modelo > 0:
        try:
            modelo = Modelos.objects.get(pk=id_modelo)
            f_modelo = ModelosForm( request.POST, instance=modelo)
            if f_modelo.is_valid():
                f_modelo.save()
                f_modelo = ModelosForm()
        except:
            pass
        return redirect("modelos")

    else:
        f_modelo = ModelosForm(request.POST)
        if f_modelo.is_valid():
            f_modelo.save()
            f_modelo = ModelosForm()
        return redirect("modelos")

@login_required(login_url='login_tk')
def rm_modelos(request, id_modelo):
    try:
        Modelos.objects.get(pk=id_modelo).delete()
    except:
        pass

    return redirect("modelos")
