# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   28-Sep-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 01-Feb-2018
# @License: Apache license vesion 2.0

from django import forms
from .clientes import *
from .productos import *
from .categorizacion import *
from .taller import *
from .compras import *
from .ventas import *
from .presupuesto import *
from .proveedores import *
from .documentos import *

class LoginForm(forms.Form):
    username = forms.CharField(label="Nombre", max_length=200)
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput())

class ResetPasswordForm(forms.Form):
    old_password = forms.CharField(label="Contraseña antigua", widget=forms.PasswordInput())
    password = forms.CharField(label="Contraseña nueva", widget=forms.PasswordInput())
    repite = forms.CharField(label="Contraseña nueva", widget=forms.PasswordInput())


from django.contrib.auth.models import User
from adminshop.models import ConfigSite

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', "first_name",  "is_superuser")
        labels = {
            "is_superuser": "Es administrador",
            "username": "Nombre usuario o NICK",
            "first_name": "Nombre completo"
        }


class ConfigSiteForm(forms.ModelForm):
    class Meta:
        model = ConfigSite
        exclude = []
