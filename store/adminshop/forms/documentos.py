# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   01-Feb-2018
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 01-Feb-2018
# @License: Apache license vesion 2.0


from django import forms

class RangoPolicia(forms.Form):
    fecha_inicio = forms.DateField()
    fecha_fin = forms.DateField()
