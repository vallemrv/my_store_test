# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   27-Aug-2017
# @Email:  valle.mrv@gmail.com
# @Filename: admin_extras.py
# @Last modified by:   valle
# @Last modified time: 24-Mar-2018
# @License: Apache license vesion 2.0


from django import template
from adminshop.models import (LineasVentas, LineasPresupuesto, LineasAbonos,
                              ConfigSite, Presupuesto)
import os

register = template.Library()

@register.filter(name='file_exist')
def file_exist(path, file):
    full_path = os.path.join(path, str(file))
    return os.path.isfile(full_path)


@register.filter(name='dni_compra')
def dni_compra(p):
    vendedor = p.get_vendedor()
    if "DNI" in vendedor:
        return vendedor["DNI"]
    else:
        return ""

@register.filter(name='p_unidad')
def p_unidad(p, regimen):
    if regimen == "ISP":
        iva = ConfigSite.objects.all()[0].ISP
        el_cien = iva + 100.00
        return "{0:.2f}".format((float(p.p_unidad) * (100.00)) /  el_cien)
    return "%.2f" % p.p_unidad

@register.filter(name='isp_str')
def isp_str(total):
    iva = ConfigSite.objects.all()[0].ISP
    el_cien = iva + 100
    base = (float(total) * (100.00)) /  el_cien
    parte_iva = float(total) - base

    return "S.TOTAL: {0:.2f}€ + {2}% IVA: {1:.2f}€".format(base, parte_iva, iva)


@register.filter(name='total')
def total(p, regimen):
    precio_unidad = p.p_unidad
    descuento = 1 - (float(p.descuento )/ 100.00)
    if regimen == "ISP":
        iva = ConfigSite.objects.all()[0].ISP
        el_cien = iva + 100
        precio_unidad = (float(p.p_unidad )* (100.00)) /  el_cien
    return "{0:.2f}".format(float(p.can) * float(precio_unidad) * float(descuento))

@register.filter(name='total_sin_iva')
def total_sin_iva(p):
    precio_unidad = p.p_unidad
    descuento = 1 - (float(p.descuento )/ 100.00)
    iva = ConfigSite.objects.all()[0].ISP
    el_cien = iva + 100
    precio_unidad = (float(p.p_unidad )* (100.00)) /  el_cien
    return "{0:.2f}".format(float(p.can) * float(precio_unidad) * float(descuento))

@register.filter(name='precio_sin_iva')
def precio_sin_iva(p):
    iva = ConfigSite.objects.all()[0].ISP
    el_cien = iva + 100.00
    return "{0:.2f}".format((float(p.p_unidad) * (100.00)) /  el_cien)


@register.filter(name='total_factura')
def total_factura(p):
    lineas =  LineasVentas.objects.filter(venta__pk=p.pk)
    total = 0
    for l in lineas:
        descuento = 1 - (float(l.descuento)/100.00)
        total += float(l.can) * float(l.p_unidad) * float(descuento)
    return "{0:.2f}".format(total)

@register.filter(name='total_abono')
def total_abono(p):
    lineas =  LineasAbonos.objects.filter(abono__pk=p.pk)
    total = 0
    for l in lineas:
        descuento = 1 - (l.descuento/100)
        total += float(l.can) * float(l.p_unidad) * float(descuento)
    return "{0:.2f}".format(total)

@register.filter(name='total_pres')
def total_pres(p):
    descuento = 1 - (float(p.descuento) / 100.00)
    return "{0:.2f}".format(float(p.can) * float(p.precio) * float(descuento))

@register.filter(name='total_pres_doc')
def total_pres_doc(p):
    lineas =  LineasPresupuesto.objects.filter(presupuesto__pk=p.pk)
    total = 0
    for l in lineas:
        descuento = 1 - (float(l.descuento)/100.00)
        total += float(l.can) * float(l.precio) * float(descuento)
    return "{0:.2f}".format(total)

@register.filter(name='DNI')
def DNI_compra(p):
    return p.get_vendedor()['DNI']

@register.filter(name='path_firma')
def path_firma(firma):
    if firma == "":
        return firma
    return "firmas/%s" % firma

@register.filter(name='detalle')
def detalle(p):
    if "IMEI" in p.detalle:
        return p.detalle
    elif p.codigo_compra == p.ns_imei:
        return p.detalle
    else:
        return p.detalle + " Ns o IMEI: "+p.ns_imei

@register.filter(name='es_cero')
def es_cero(v):
    if float(v) <= 0:
        return True
    else:
        return False


@register.filter(name='producto')
def producto(pk):
    ps = Presupuesto.objects.filter(factura_id=pk)
    if len(ps):
        return ps[0].producto


@register.filter(name='ns_imei')
def ns_imei(pk):
    ps = Presupuesto.objects.filter(factura_id=pk)
    if len(ps):
        return ps[0].producto.ns_imei

@register.filter(name='detalle_cliente')
def detalle_cliente(pk):
    ps = Presupuesto.objects.filter(factura_id=pk)
    if len(ps):
        return ps[0].notas_cliente
