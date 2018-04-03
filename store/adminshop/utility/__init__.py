# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   02-Dec-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 11-Jan-2018
# @License: Apache license vesion 2.0

from .doc_pdf import *
from .calculos import *
from adminshop.models import (Historial, DocumentoTesteo, Firmas)


def save_historial(user_id, cliente_id, producto_id, men):
    historial = Historial()
    historial.cliente_id = cliente_id
    historial.producto_id = producto_id
    historial.usuario_id = user_id
    historial.detalle = men
    historial.save()
    return historial

def save_doc_testeo(user_id, cliente_id, producto_id):
    doc = DocumentoTesteo()
    doc.cliente_id = cliente_id
    doc.producto_id = producto_id
    doc.empleado_id = user_id
    doc.save()
    return doc

def save_doc_firmas(user_id, doc_id, tipo):
    firma = Firmas()
    firma.empleado_id = user_id
    firma.documento_id = doc_id
    firma.tipo_documento = tipo
    firma.save()
    return firma
