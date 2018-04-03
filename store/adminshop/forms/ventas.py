# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   28-Sep-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 31-Jan-2018
# @License: Apache license vesion 2.0

from django import forms
from adminshop.models import ( Ventas, Productos, Garantias)


class VentasForm(forms.ModelForm):
    class Meta:
        model = Ventas
        fields = "__all__"

class GarantiasForm(forms.ModelForm):
    class Meta:
        model = Garantias
        fields = ["documento"]
        widgets = {
            'documento': forms.FileInput(attrs={'accept':'application/pdf'})
        }


class ProdutoSimpleForm(forms.ModelForm):
    class Meta:
        model= Productos
        exclude = ["tipo", "precio_compra", "color",
                   "descuento", "descripcion", "estado"]
        labels = {
            "detalle": "Descripción"
        }
