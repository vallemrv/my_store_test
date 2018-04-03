# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   27-Aug-2017
# @Email:  valle.mrv@gmail.com
# @Filename: admin_extras.py
# @Last modified by:   valle
# @Last modified time: 02-Feb-2018
# @License: Apache license vesion 2.0

from django import template
from django.db.models import Q
try:
    from django.core.urlresolvers import reverse
except ImportError:
    from django.urls import reverse

from adminshop.models import Testeo, Compras, Presupuesto
import json
import sys
register = template.Library()


@register.filter(name='get_nombre_cliente')
def get_nombre_cliente(f):
    return f.get_nombre_cliente()

@register.filter(name='enviado')
def enviado(f):
    return "No" if not f.enviado else "Si"


@register.filter(name='get_user')
def get_user(f):
    return f.get_user()

@register.filter(name='get_ns_imei')
def get_ns_imei(f):
    return f.get_ns_imei()

@register.filter(name='get_producto_pk')
def get_producto_pk(f):
    return f.get_producto_pk()


@register.filter(name='addcss')
def addcss(field, css):
    return field.as_widget(attrs={"class":css})

@register.filter(name='reparacion')
def reparacion(p):
    try:
        pres = Presupuesto.objects.filter(producto__pk=p.id)[0]
        return pres.notas_cliente
    except:
        return ""

@register.filter(name='num_pres')
def num_pres(p):
    try:
        pres = Presupuesto.objects.filter(producto__pk=p.id)[0]
        return pres.pk
    except:
        return -1

@register.filter(name='precio_venta')
def precio_venta(p):
    precio =  0 if p.precio_venta == None else p.precio_venta
    return "{0:.2f} €".format(precio)

@register.filter(name='precio_usado')
def precio_usado(p):
    return "{0:.2f} €".format(p.modelo.precio_usado * p.tipo.incremento)

@register.filter(name='document_show')
def document_show(p):
    compras = Compras.objects.filter(producto__id=p.pk)
    if len(compras) > 0:
        compra = compras[0]
    else:
        compra = Compras()
    return p.estado in ["ST", "VD", "OL", "VT"]

@register.filter(name='document_href')
def document_href(p):
    if p.estado in ["ST", "VT", "OL"]:
        return reverse("get_document_by_id", args=[p.pk])
    elif p.estado in ["RP", "OK", "PD"]:
        return reverse("get_presupuesto_pdf", args=[p.pk])
    elif p.estado == "VD":
        return reverse("get_all_document", args=[p.pk])
    else:
        return "#"

@register.filter(name='have_sign')
def have_sign(p):
    compras = Compras.objects.filter(producto__id=p.pk)
    compra = Compras()
    if len(compras) > 0:
        compra = compras[0]
    return p.estado in ["ST", "VD", "OL", "VT"] and compra.firma == ""

@register.filter(name='editable')
def editable(p):
    return p.estado in ["ST", "OL", "VT"]


@register.simple_tag(name='get_estado_value')
def get_estado_value(test_id, p_id, estado):
    testeos = Testeo.objects.filter(Q(descripcion__pk=test_id) &
                                    Q(producto__pk=p_id))
    send = ""
    if len(testeos) > 0 and testeos[0].estado == estado:
        send = "selected"

    return send

@register.filter(name='addattrs')
def addattrs(field, args):
    attr = {}
    try:
        args_parse = args.replace("'", '"')
        attr = json.loads(args_parse)
    except Exception as error:
        print(error)
    return field.as_widget(attrs=attr)

@register.filter('klass')
def klass(ob):
    return ob.field.widget.__class__.__name__


@register.filter('display')
def display(form, value):
    return dict(form.field.choices)[value]

@register.filter('modelo')
def modelo(p):
    if p.modelo != None:
        return str(p.modelo)
    else:
        return p.detalle


@register.filter('marca')
def marca(p):
    if p.modelo != None:
        return str(p.modelo.marca)
    else:
        return ""
