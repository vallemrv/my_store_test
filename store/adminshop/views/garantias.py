# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   05-Dec-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 31-Jan-2018
# @License: Apache license vesion 2.0


from django.db.models import Q
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
try:
    from django.core.urlresolvers import reverse
except ImportError:
    from django.urls import reverse

from django.contrib.auth.decorators import login_required, permission_required
from adminshop.models import Garantias
from adminshop.forms import GarantiasForm
import os


@login_required(login_url='login_tk')
def garantias(request, id_garantia=-1):
    if not request.method == "POST" and id_garantia == -1:
        form = GarantiasForm()
        return render(request, "tienda/garantias/garantias.html",
                      {"form": form,
                       "garantias": Garantias.objects.all(),
                       "mensaje": "Garantia nueva"})
    elif not request.method == "POST" and id_garantia > 0:
        form = GarantiasForm()
        try:
            garantia = Garantias.objects.get(pk=id_garantia)
            form = GarantiasForm(instance=garantia)
        except:
            pass


        return render(request, "tienda/garantias/garantias.html",
                      {"form": form,
                       "garantias": Garantias.objects.all(),
                       "mensaje": "Editar Garantia"})

    elif id_garantia > 0:
        try:
            garantia = Garantias.objects.get(pk=id_garantia)
            form = GarantiasForm(request.POST, request.FILES, instance=garantia)
            if form.is_valid():
                form.save()

        except:
            pass
        return redirect("garantias_none")

    else:
        form = GarantiasForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            form = GarantiasForm()
        return render(request, "tienda/garantias/garantias.html",
                      {"form": form,
                       "garantias": Garantias.objects.all(),
                       "mensaje": "Garantias nueva"})


@login_required(login_url='login_tk')
def lista_garantias(request):
    if request.method == "POST":
        filter = request.POST["filter"]
        filter_query = Garantias.objects.filter(Q(documento__icontains=filter))
        return render(request, "tienda/garantias/lista_ajax.html",
                      {'garantias': filter_query,})



@login_required(login_url='login_tk')
def rm_garantia(request, id_garantia):
    try:
        Garantias.objects.get(pk=id_garantia).delete()
    except:
        pass

    return redirect("garantias_none")


@login_required(login_url='login_tk')
def get_documento_garantia(request, id_garantia):
    from adminshop.utility import get_documento_garantia as get_documento
    response = HttpResponse(content_type='application/pdf')
    garantia = Garantias.objects.get(pk=id_garantia)
    doc_garantia = get_documento(garantia)
    response.write(doc_garantia.getvalue())
    return response
