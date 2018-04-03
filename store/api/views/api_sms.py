# -*- coding: utf-8 -*-
# @Author: Manuel Rodriguez <valle>
# @Date:   17-Oct-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 31-Dec-2017
# @License: Apache license vesion 2.0
from django.db.models import Q
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt
from tokenapi.decorators import token_required
from tokenapi.http import  JsonError, JsonResponse
from adminshop.models import  Clientes
import base64
import os



# Create your views here.
@csrf_exempt
def get_all_telf(request):
    clientes = Clientes.objects.all().exclude(Q(telefono="") | Q(telefono=None))
    cl_send = []
    for c in clientes:
        cl_send.append({"telefono": c.telefono})
    return JsonResponse(cl_send)
