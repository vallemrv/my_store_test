# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   28-Sep-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 15-Dec-2017
# @License: Apache license vesion 2.0

from django import forms
from adminshop.models import (Compras, Productos)

# este formulario lo utiliza las (compras, )
class CPProductosForm(forms.ModelForm):
    class Meta:
        model = Productos
        fields = ["ns_imei", "color",]

class FinTratoForm(forms.ModelForm):
    class Meta:
        model = Productos
        fields = ["tipo",  "precio_compra"]
        widgets = {
            'tipo': forms.Select(attrs={'onchange': "get_precio();", "value": "1"},),
            }


class VistaValidarForm(forms.ModelForm):
    class Meta:
        model = Compras
        exclude = ["firma", "vendedor_id", 'tipo_vendedor', "usuario", "tipo_compra", "doc_proveedor"]
        widgets = {
            'producto': forms.Select(attrs={"disabled":True}),
        }

class ValidarCompra(forms.ModelForm):

    class Meta:
        model = Compras
        fields = ["codigo_compra"]

class FirmaCompra(forms.ModelForm):
    class Meta:
        model = Compras
        fields = ["firma"]


class MODProductosForm(forms.ModelForm):
    cliente = forms.IntegerField(widget=forms.HiddenInput())
    class Meta:
        model = Productos
        fields = [ "modelo",'tipo', "ns_imei", "color", 'precio_compra']
        widgets = {
            'tipo': forms.Select(attrs={'onchange': "get_precio();", "value": "1"},),
            "modelo": forms.HiddenInput()
        }
