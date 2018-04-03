# -*- coding: utf-8 -*-
# @Author: Manuel Rodriguez <valle>
# @Date:   17-Oct-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 02-Dec-2017
# @License: Apache license vesion 2.0
from django.db.models import Q
from django.conf import settings
from django.forms.models import model_to_dict
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from tokenapi.decorators import token_required
from tokenapi.http import  JsonError, JsonResponse
from adminshop.models import Compras, Clientes, Presupuesto, Firmas, DocumentoTesteo
import base64
import os



# Create your views here.
@csrf_exempt
def get_documento_firma(request):
    if request.method == "POST":
        dni = request.POST["data"]
        clientes = Clientes.objects.filter(DNI=dni)
        pk = -1
        if len(clientes) >0:
            pk =  clientes[0].pk
        compras = Compras.objects.filter(Q(vendedor_id=pk) & Q(firma=""))
        if len(compras) > 0:
            vendedor = compras[0].get_vendedor()
            producto = compras[0].producto
            return JsonResponse({"result":
                                 [{"nombre": cliente.nombre_completo,
                                   "compra_id": compras[0].id,
                                   "nombre": vendedor["nombre"],
                                   "telefono": vendedor['telefono'],
                                   "DNI": vendedor["DNI"].upper(),
                                   "domicilio": vendedor['domicilio'],
                                   "modelo": str(producto),
                                   "ns_imei": producto.ns_imei,
                                   "precio": producto.precio_compra}]})
        else:
            return JsonResponse({"result": []})
    else:
        return JsonError("Solo acepta peticiones POST")


@csrf_exempt
def set_firma(request, id_compra, dni):
    path_file = os.path.join(settings.BASE_DIR, "firmas/compras")
    file_name = "{0}_{1}.jpg".format(dni, id_compra)
    file = open(os.path.join(path_file, file_name), "wb")
    file_data = request.POST['file']
    file_data = base64.b64decode(file_data.split(",")[1])
    file.write(file_data)
    file.close()
    compra = Compras.objects.get(id=id_compra)
    compra.firma = file_name
    compra.save()
    return JsonResponse({"result": True})


@csrf_exempt
def set_firma_compra_insitu(request, id_compra, dni):
    path_file = os.path.join(settings.BASE_DIR, "firmas/compras")
    file_name = "{0}_{1}.jpg".format(dni, id_compra)
    file = open(os.path.join(path_file, file_name), "wb")
    file_data = request.POST['file']
    file_data = base64.b64decode(file_data.split(",")[1])
    file.write(file_data)
    file.close()
    compra = Compras.objects.get(id=id_compra)
    compra.firma = file_name
    compra.save()
    firmas = Firmas.objects.filter(Q(documento_id=id_compra)&
                                  Q(tipo_documento="CP") &
                                  Q(firmado=False))
    if len(firmas) > 0:
        firmas[0].firmado = True
        firmas[0].save()
    return JsonResponse({"result": True})


@csrf_exempt
def set_firma_press_insitu(request, id_press, dni):
    path_file = os.path.join(settings.BASE_DIR, "firmas/presupuestos")
    file_name = "{0}_{1}.jpg".format(dni, id_press)
    file = open(os.path.join(path_file, file_name), "wb")
    file_data = request.POST['file']
    file_data = base64.b64decode(file_data.split(",")[1])
    file.write(file_data)
    file.close()
    p = Presupuesto.objects.get(id=id_press)
    p.firma = file_name
    p.save()
    firmas = Firmas.objects.filter(Q(documento_id=id_press)&
                                  Q(tipo_documento="RP")&
                                  Q(firmado=False))
    if len(firmas) > 0:
        firmas[0].firmado = True
        firmas[0].save()
    return JsonResponse({"resutl": True})



@csrf_exempt
def set_firma_testeo_insitu(request, id_test, dni):
    path_file = os.path.join(settings.BASE_DIR, "firmas/testeo")
    file_name = "{0}_{1}.jpg".format(dni, id_test)
    file = open(os.path.join(path_file, file_name), "wb")
    file_data = request.POST['file']
    file_data = base64.b64decode(file_data.split(",")[1])
    file.write(file_data)
    file.close()
    p = DocumentoTesteo.objects.get(id=id_test)
    p.firma = file_name
    p.save()
    firmas = Firmas.objects.filter(Q(documento_id=id_test)&
                                      Q(tipo_documento="OS")&
                                      Q(firmado=False))
    if len(firmas) > 0:
        firmas[0].firmado = True
        firmas[0].save()
    return JsonResponse({"result": True})
