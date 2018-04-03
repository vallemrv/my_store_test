# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   28-Sep-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 29-Sep-2017
# @License: Apache license vesion 2.0


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from adminshop.forms import AlmacenesForm, TiposForm
from adminshop.models import Almacenes, Tipos

@login_required(login_url='login_tk')
def almacenes(request, id_almacen=-1):
    if not request.method == "POST" and id_almacen == -1:
        f_almacen = AlmacenesForm()
        return render(request, "gestion/almacenes.html",
                      {"form": f_almacen,
                       "almacenes": Almacenes.objects.all(),
                       "mensaje": "Almacen nuevo"})
    elif not request.method == "POST" and id_almacen > 0:
        f_almacen = AlmacenesForm()
        try:
            catergoria = Almacenes.objects.get(pk=id_almacen)
            f_almacen = AlmacenesForm(instance=catergoria)
        except:
            pass


        return render(request, "gestion/almacenes.html",
                      {"form": f_almacen,
                       "almacenes": Almacenes.objects.all(),
                       "mensaje": "Editar almacen"})

    elif id_almacen > 0:
        try:
            catergoria = Almacenes.objects.get(pk=id_almacen)
            f_almacen = AlmacenesForm( request.POST, instance=catergoria)
            if f_almacen.is_valid():
                f_almacen.save()
                f_almacen = AlmacenesForm()
        except:
            pass
        return redirect("almacenes")

    else:
        f_almacen = AlmacenesForm(request.POST)
        if f_almacen.is_valid():
            f_almacen.save()
            f_almacen = AlmacenesForm()
        return redirect("almacenes")

@login_required(login_url='login_tk')
def rm_almacenes(request, id_almacen):
    try:
        Almacenes.objects.get(pk=id_almacen).delete()
    except:
        pass

    return redirect("almacenes")

@login_required(login_url='login_tk')
def tipos(request, id_tipo=-1):
    if not request.method == "POST" and id_tipo == -1:
        f_tipo = TiposForm()
        return render(request, "gestion/tipo_usados.html",
                      {"form": f_tipo,
                       "tipos": Tipos.objects.all(),
                       "mensaje": "Tipo nuevo"})
    elif not request.method == "POST" and id_tipo > 0:
        f_tipo = TiposForm()
        try:
            catergoria = Tipos.objects.get(pk=id_tipo)
            f_tipo = TiposForm(instance=catergoria)
        except:
            pass


        return render(request, "gestion/tipo_usados.html",
                      {"form": f_tipo,
                       "tipos": Tipos.objects.all(),
                       "mensaje": "Editar tipo"})

    elif id_tipo > 0:
        try:
            catergoria = Tipos.objects.get(pk=id_tipo)
            f_tipo = TiposForm( request.POST, instance=catergoria)
            if f_tipo.is_valid():
                f_tipo.save()
                f_tipo = TiposForm()
        except:
            pass
        return redirect("tipo_usados")

    else:
        f_tipo = TiposForm(request.POST)
        if f_tipo.is_valid():
            f_tipo.save()
            f_tipo = TiposForm()
        return redirect("tipo_usados")

@login_required(login_url='login_tk')
def rm_tipos(request, id_tipo):
    try:
        Tipos.objects.get(pk=id_tipo).delete()
    except:
        pass

    return redirect("tipo_usados")
