# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   28-Sep-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 18-Dec-2017
# @License: Apache license vesion 2.0

from django import forms
from adminshop.models import Clientes, Proveedores, Direcciones
from uuid import uuid4

class ClientesForm(forms.ModelForm):
    class Meta:
        model = Clientes
        exclude = ['password', "activo"]


class ProveedoresForm(forms.ModelForm):
    class Meta:
        model = Proveedores
        exclude = ["nombre", "activo"]

class DireccionesForm(forms.ModelForm):
    class Meta:
        model = Direcciones
        exclude = ["cliente"]


class CPClientesForm(forms.ModelForm):
    direccion = forms.CharField(required=False, widget=forms.TextInput(attrs={'autocomplete':str(uuid4())}))
    localidad =  forms.CharField(required=False, widget=forms.TextInput(attrs={'autocomplete':str(uuid4())}))
    codigo_postal =  forms.CharField(required=False, widget=forms.TextInput(attrs={'autocomplete':str(uuid4())}))
    provincia =  forms.CharField(required=False, widget=forms.TextInput(attrs={'autocomplete':str(uuid4())}))

    class Meta:
        model = Clientes
        fields = ["DNI", "nombre_completo", "email", "telefono",
                  "direccion", "localidad", "codigo_postal", "provincia", "nota"]
        widgets = {
            "DNI": forms.TextInput(attrs={"required":True}),
            "nombre_completo": forms.TextInput(attrs={'autocomplete':str(uuid4())}),
            "email" : forms.TextInput(attrs={'autocomplete':str(uuid4())}),
            "telefono": forms.TextInput(attrs={'autocomplete':str(uuid4())}),
            "nota": forms.Textarea()
        }
