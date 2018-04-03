# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   28-Sep-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 07-Feb-2018
# @License: Apache license vesion 2.0

from django.db.models import Q
from django.forms.models import model_to_dict
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from adminshop.forms import  (ClientesForm, DireccionesForm,
                              CPClientesForm)
from adminshop.models import  Clientes, Direcciones


@login_required(login_url='login_tk')
def clientes(request, id_cliente=-1):
    if not request.method == "POST" and id_cliente == -1:
        f_cliente = CPClientesForm()
        return render(request, 'gestion/clientes/clientes.html',
                      {"form": f_cliente,
                       "titulo": "Cliente nuevo" })

    elif not request.method == "POST" and id_cliente > 0:
        f_cliente = CPClientesForm()
        try:
            clientes = Clientes.objects.filter(pk=id_cliente)
            if len(clientes) > 0:
                cliente = clientes[0]
            else:
                cliente = Clientes()
            direccion = get_first_direccion(id_cliente)
            full_data = dict(model_to_dict(direccion).items() + model_to_dict(cliente).items())
            f_cliente = CPClientesForm (full_data, instance=cliente)
        except:
            print("Error al enviar formulario")

        return render(request, 'gestion/clientes/clientes.html',
                      {"form": f_cliente,
                       "id_cliente": id_cliente,
                       "titulo": "Editar cliente" })
    elif id_cliente > 0:
        cliente = None
        clientes = Clientes.objects.filter(pk=id_cliente)
        if len(clientes) > 0:
            cliente = clientes[0]
        cliente = modificar_cliente(request.POST, cliente)

        return redirect("lista_clientes")
    else:
        cliente = modificar_cliente(request.POST)
        return redirect("lista_clientes")

@login_required(login_url='login_tk')
def rm_clientes(request, id_cliente):
    try:
        for c in Clientes.objects.filter(pk=id_cliente):
            c.activo = False
            c.save()
    except:
        pass

    return redirect("lista_clientes")

@login_required(login_url='login_tk')
def edit_direcciones(request, id_direccion):
    if not request.method == "POST":
        f_direccion = DireccionesForm()
        try:
            direccion = Direcciones.objects.get(pk=id_direccion)
            f_direccion = DireccionesForm(instance=direccion)
        except:
            pass

        return render(request, 'gestion/clientes/direcciones.html',
                      {"form": f_direccion,
                       "titulo": "Editar direccion" })
    else:
        f_direccion = DireccionesForm()
        try:
            direccion = Direcciones.objects.get(pk=id_direccion)
            f_direccion = DireccionesForm(request.POST, instance=direccion)
        except:
            pass

        if f_direccion.is_valid():
            direccion = f_direccion.save()
        return redirect("lista_clientes")

@login_required(login_url='login_tk')
def direcciones(request, id_cliente=-1):
    if not request.method == "POST" and id_cliente == -1:
        f_cliente = ClientesForm()
        return render(request, 'gestion/clientes/clientes.html',
                      {"form": f_cliente,
                       "titulo": "Cliente nuevo" })
    elif id_cliente > 0:
        f_cliente = ClientesForm()
        try:
            clientes = Clientes.objects.filter(pk=id_cliente)
            if len(clientes) > 0:
                cliente = clientes[0]
            else:
                cliente = Clientes()
            f_cliente = ClientesForm(instance=cliente)
        except:
            pass
        f_direccion = DireccionesForm(request.POST)
        if f_direccion.is_valid():
            direccion = f_direccion.save(commit=False)
            direccion.cliente_id = id_cliente
            direccion.save()
        return redirect("lista_clientes")
    else:
        return redirect("clientes")

@login_required(login_url='login_tk')
def rm_direcciones(request, id_direccion):
    try:
        id_cliente = -1
        direccion = Direcciones.objects.get(pk=id_direccion)
        id_cliente = direccion.cliente_id
        direccion.delete()
    except:
        pass

    return redirect("clientes", id_cliente=str(id_cliente))

@login_required(login_url='login_tk')
def lista_clientes(request):
    if request.method == "POST":
        filter = request.POST["filter"]
        filter_query = Clientes.objects.filter(Q(nombre_completo__icontains=filter) |
                                               Q(DNI__icontains=filter) |
                                               Q(telefono__contains=filter)).exclude(activo=False)
        return render(request, "gestion/clientes/lista_clientes.html", {'query': filter_query})
    else:
        filter_query = Clientes.objects.all().exclude(activo=False)
        return render(request, "gestion/clientes/lista_clientes.html", {'query': filter_query})

@login_required(login_url='login_tk')
def al_find_cliente(request):
    if request.method == "POST":
        filter = request.POST["filter"]
        filter_query = Clientes.objects.filter(Q(nombre_completo__contains=filter) |
                                               Q(DNI__contains=filter) |
                                               Q(telefono__contains=filter)).exclude(activo=False)
        f_cliente = CPClientesForm()
        return render(request, "gestion/clientes/lista_ajax.html",
                      {'query': filter_query,
                       'form': f_cliente})
    return redirect("gestion")

@login_required(login_url='login_tk')
def save_cliente(request):
    from tokenapi.http import JsonResponse
    cliente = modificar_cliente(request.POST)
    return JsonResponse({'id': cliente.id})


def modificar_cliente(datos, cliente=None):
    if cliente != None:
        form = CPClientesForm(datos, instance=cliente)
    else:
        form = CPClientesForm(datos)

    if form.is_valid():
        cliente = form.save()
        direccion = set_first_direccion(datos, cliente.pk)
        direccion.cliente_id = cliente.pk
        direccion.save()
    else:
        print(form.errors)

    return cliente

def validoDNI(dni):
    if dni[0].isalpha():
        return True
    tabla = "TRWAGMYFPDXBNJZSQVHLCKE"
    dig_ext = "XYZ"
    reemp_dig_ext = {'X':'0', 'Y':'1', 'Z':'2'}
    numeros = "1234567890"
    dni = dni.upper()
    if len(dni) == 9:
        dig_control = dni[8]
        dni = dni[:8]
        if dni[0] in dig_ext:
            dni = dni.replace(dni[0], reemp_dig_ext[dni[0]])
        return len(dni) == len([n for n in dni if n in numeros]) \
            and tabla[int(dni)%23] == dig_control
    return False

def set_first_direccion(datos, cliente_id):
    direccion = Direcciones.objects.filter(cliente_id=cliente_id)
    if len(direccion) > 0:
        f_direccion = DireccionesForm(datos, instance=direccion[0])
    else:
        f_direccion = DireccionesForm(datos)

    if f_direccion.is_valid():
        direccion = f_direccion.save(commit=False)
    else:
        print(f_direccion.errors)
    return direccion

def get_first_direccion(cliente_id):
    direccion = Direcciones.objects.filter(cliente_id=cliente_id)
    if len(direccion) > 0:
        return direccion[0]
    else:
        return Direcciones()
