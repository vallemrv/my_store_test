# @Author: Manuel Rodriguez <valle>
# @Date:   28-Sep-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 28-Sep-2017
# @License: Apache license vesion 2.0


from django import forms
from adminshop.models import (Almacenes, Tipos)

class AlmacenesForm(forms.ModelForm):
    class Meta:
        model = Almacenes
        exclude = []

class TiposForm(forms.ModelForm):
    class Meta:
        model = Tipos
        exclude = []
