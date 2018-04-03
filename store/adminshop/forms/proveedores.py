# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   28-Sep-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 20-Jan-2018
# @License: Apache license vesion 2.0

from django import forms
from adminshop.models import Proveedores, Productos, Compras


class ProveedoresForm(forms.ModelForm):
    class Meta:
        model = Proveedores
        exclude = ["nombre", "activo"]

class ProveedorCompra(forms.ModelForm):
    tipo_compra = forms.ChoiceField(choices=[(None,"-------------"), ("REBU","REBU"), ("ISP","ISP")], initial=None)

    class Meta:
        model = Compras
        exclude = ["vendedor_id", "tipo_vendedor", "firma", "usuario", "producto" ]
        widgets = {
            'doc_proveedor': forms.FileInput(attrs={'required': 'true'}),
        }
