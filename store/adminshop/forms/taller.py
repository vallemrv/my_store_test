# @Author: Manuel Rodriguez <valle>
# @Date:   28-Sep-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 09-Nov-2017
# @License: Apache license vesion 2.0


from django import forms
from adminshop.models import (Productos, Reparaciones)

class ActuacionesForm(forms.ModelForm):
    class Meta:
        model = Reparaciones
        exclude = []
        

class FinTesteoForm(forms.ModelForm):
    class Meta:
        model = Productos
        fields = ["tipo"]
