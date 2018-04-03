# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   28-Sep-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 20-Jan-2018
# @License: Apache license vesion 2.0

from django import forms
from adminshop.models import (Categorias, Marcas, Modelos, Compras,
                              Productos, ListaTesteo)

class CategoriasForm(forms.ModelForm):
    class Meta:
        model = Categorias
        exclude = []
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'})
        }

class MarcasForm(forms.ModelForm):
    class Meta:
        model = Marcas
        exclude = []

class ModelosForm(forms.ModelForm):
    class Meta:
        model = Modelos
        exclude = []
        widgets = {
            'nombre': forms.TextInput(attrs={'required': 'true'}),
        }

class TipoTesteoForm(forms.ModelForm):
    class Meta:
        model = ListaTesteo
        exclude = []

class EditProductoForm(forms.ModelForm):
    estado = forms.ChoiceField(choices=(("ST","En stock"), ("VT","En venta"), ("OL","Venta online")))
    class Meta:
        model = Productos
        exclude = ["tipo", "precio_compra", "es_unico", "detalle",
                   "modelo", "color", "ns_imei",  "fecha_salida", "descuento"]


class ComplementosForm(forms.ModelForm):
    class Meta:
        model = Productos
        fields = ["ns_imei", "detalle", "precio_venta", "descuento"]



class ProductosForm(forms.ModelForm):
    class Meta:
        model = Productos
        fields = ['modelo', 'tipo', "ns_imei", "color", 'precio_compra']
        widgets = {
            'tipo': forms.Select(attrs={'onchange': "get_precio();", "value": "1",  'required': 'true'},),
            "modelo" : forms.Select(attrs={"disabled": True}),
        }


class EstadoProductosForm(forms.ModelForm):
    class Meta:
        model = Productos
        fields = ['estado']
