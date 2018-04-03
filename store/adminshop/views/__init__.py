# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   28-Sep-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 31-Jan-2018
# @License: Apache license vesion 2.0


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.template import RequestContext
from django.contrib.auth import login as login_auth, logout as logout_auth, authenticate
from adminshop.forms import LoginForm, ConfigSiteForm
from adminshop.models import ConfigSite
from .categorias import *
from .clientes import *
from .categorizacion import *
from .productos import *
from .usuarios import *
from .compras import *
from .taller import *
from .ventas import *
from .abonos import *
from .presupuesto import *
from .sign import *
from .proveedores import *
from .garantias import *
from .balances import *
from .documentos import *


# Create your views here.
@login_required(login_url='login_tk')
def tienda(request):
    return render(request, "menus/tienda.html")

@login_required(login_url='login_tk')
def taller(request):
    return render(request, "menus/taller.html")

@login_required(login_url='login_tk')
def gestion(request):
    return render(request, "menus/gestion.html")

@login_required(login_url='login_tk')
def informes(request):
    return render(request, "menus/informes.html")

@login_required(login_url='login_tk')
def almacen(request):
    return render(request, "menus/almacen.html")

@login_required(login_url='login_tk')
def configuracion(request):
    if not request.method == "POST":
        f_categoria = CategoriasForm()
        try:
            config = ConfigSite.objects.get(pk=1)
            f_config = ConfigSiteForm(instance=config)
        except:
            config = ConfigSite(codigo_compra="4000")
            config.save()
            f_config = ConfigSiteForm(instance=config)

        return render(request, "gestion/configuracion.html",
                      {"form": f_config,
                       "mensaje": "Editar configuracion"})

    else:
        config = ConfigSite.objects.get(pk=1)
        f_config = ConfigSiteForm(request.POST, request.FILES, instance=config)
        if f_config.is_valid():
            f_config.save()
        else:
            print(f_config.errors)
        return redirect("gestion")


def login(request):
    if not request.method == "POST":
        #if request.user.is_authenticated:
        #    return redirect("/gestion")
        form_log = LoginForm()
        return render(request, "gestion/login/login.html", {"form": form_log})
    else:
        form_log = LoginForm(request.POST)
        if form_log.is_valid():
            user = authenticate(username=form_log.cleaned_data['username'],
                                password=form_log.cleaned_data['password'])
            if user != None:
                login_auth(request, user)
                return redirect("tienda")
            else:
                return render(request, "gestion/login/login.html",
                              {"form": form_log, "mensaje": "El usuario o la contraseña no son validos"})

def logout(request):
    logout_auth(request)
    return redirect("tienda")

def en_construccion(request):
    return render(request, "gestion/404.html")
