# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   28-Sep-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 05-Dec-2017
# @License: Apache license vesion 2.0

from django import forms
from adminshop.models import ( Presupuesto, Productos, NotasReparacion)

class PRProductoForms(forms.ModelForm):
    observacion_cliente = forms.CharField(label="Observación del cliente", widget=forms.Textarea, required=False)
    notas_tecnico = forms.CharField(label="Anotaciones internas", widget=forms.Textarea, required=False)

    class Meta:
        model= Productos
        fields = ["ns_imei", "detalle", "observacion_cliente", ]
        labels = {
            'detalle': "Descripción modelo",
        }


class NotasReparacionForm(forms.ModelForm):
    class Meta:
        model= NotasReparacion
        fields = ["detalle"]
