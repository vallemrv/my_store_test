# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   20-Nov-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 14-Jan-2018
# @License: Apache license vesion 2.0


from django.shortcuts import render, redirect
try:
    from django.core.urlresolvers import reverse
except ImportError:
    from django.urls import reverse

from django.contrib.auth.decorators import login_required, permission_required
from django.conf import settings
from django.http import HttpResponse
from django.db.models import Q
from adminshop.models import Firmas, Compras, Presupuesto

@login_required(login_url='login_tk')
def get_sign(request):
    return render(request, "tienda/sign/sign.html")


@login_required(login_url='login_tk')
def listado_sign(request):
    return render(request, 'tienda/sign/listado.html',{
        "firmas": Firmas.objects.filter(firmado=False)
    })


@login_required(login_url='login_tk')
def rm_sign(request, id_sign):
    try:
        Firmas.objects.get(pk=id_sign).delete()
    except Exception as e:
        pass
    return redirect("listado_sign")


@login_required(login_url='login_tk')
def get_document_sign(request):
    firmas = Firmas.objects.filter(Q(empleado_id=request.user.id) &
                                   Q(firmado=False))
    if len(firmas) > 0:
        firma = firmas[0]
        template, datos =  firma.get_documento()
        if template == None:
            return HttpResponse("")
        return render(request, template, {"datos":datos})
    else:
        return HttpResponse("")
