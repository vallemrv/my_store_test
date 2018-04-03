# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   10-Jan-2018
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 16-Jan-2018
# @License: Apache license vesion 2.0

from django.db.models import Q, Sum, Count
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from adminshop.models import Ventas, Marcas, Productos
from tokenapi.http import JsonResponse, JsonError
from adminshop.utility import get_total_neto, desglose_iva
import random

@login_required(login_url='login_tk')
def balances(request):
    return render(request, "balances/balances.html")


@login_required(login_url='login_tk')
def get_ventas_chart(request):
    if request.method == "POST":
        years = 0
        month = 0
        ventas = 0
        compras = 0
        base_imponible = 0
        importe_iva = 0
        importe = 0
        try:
            years = request.POST["years"]
            month = request.POST["month"]
            ventas = Ventas.objects.filter(fecha_salida__month__gte=month,
                                           fecha_salida__year__gte=years,
                                           fecha_salida__month__lte=month,
                                           fecha_salida__year__lte=years,)


            ventas, compras = get_total_neto(ventas)
            importe = float("{0:.2f}".format((float(ventas) - float(compras))))
            base_imponible, importe_iva = desglose_iva(importe)
        except Exception as e:
            print(e)

        return JsonResponse({"years": years, "month": month, 'ventas': ventas, 'compras': float(compras),
                            "importe": importe, "beneficio": base_imponible, "iva": importe_iva})

    return JsonError("Solo peticiones post")


@login_required(login_url='login_tk')
def get_stock(request):
    labels = []
    datos = []
    color = []
    total = 0
    for marca in Marcas.objects.all():
        result = Productos.objects.filter(Q(modelo__marca=marca) &
                                          Q(estado__in=["VT", "ST", "OL"])).aggregate(Sum('precio_compra'))
        if result['precio_compra__sum'] != None:
            labels.append(marca.nombre)
            datos.append(result['precio_compra__sum'])
            total += result['precio_compra__sum']
            color.append("rgba({0}, {1}, {2}, 0.3)".format(random.randrange(255),
                                                           random.randrange(255),
                                                           random.randrange(255)))

    return JsonResponse({"labels": labels, "datos": datos, "total": total, "color": color})
