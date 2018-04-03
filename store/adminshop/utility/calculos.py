# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   11-Jan-2018
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 08-Feb-2018
# @License: Apache license vesion 2.0

from adminshop.models import (Ventas, Presupuesto, LineasVentas, Productos,
                              ConfigSite, LineasPresupuesto, Compras,
                              Modelos, Marcas)

def desglose_stock():
    pass

def desglose_iva(importe):
    iva = ConfigSite.objects.all()[0].ISP
    p_total = iva + 100.00
    base_imponible = float("{0:.2f}".format((float(importe) * (100.00)) /  p_total))
    importe_iva = float("{0:.2f}".format((base_imponible * iva) /  100.00))
    return base_imponible, importe_iva



def get_total_neto(ventas):
    total_ventas = 0
    total_compras = 0
    total_reparaciones = 0
    for v in ventas:
        lineas =  LineasVentas.objects.filter(venta__pk=v.pk)
        total = 0
        for l in lineas:
            ps = Productos.objects.filter(ns_imei__icontains=l.ns_imei)
            for p in ps:
                if p.precio_compra != None:
                    total_compras = total_compras + p.precio_compra

                descuento = 1 - (float(l.descuento)/100.00)
                total_ventas  += float(l.can) * float(l.p_unidad) * float(descuento)

    return float("%.2f" % total_ventas), total_compras
