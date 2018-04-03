# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   04-Oct-2017
# @Email:  valle.mrv@gmail.com
# @Last modified by:   valle
# @Last modified time: 02-Dec-2017
# @License: Apache license vesion 2.0

from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


class Direcciones(models.Model):
    direccion = models.CharField(max_length=200, blank=True)
    localidad =  models.CharField(max_length=50, blank=True)
    codigo_postal =  models.CharField(max_length=10, blank=True)
    provincia =  models.CharField(max_length=50, blank=True)
    es_principal = models.BooleanField(default=True)
    cliente = models.ForeignKey("Clientes", on_delete=models.CASCADE)

    def __unicode__(self):
        return self.direccion

    class Meta:
        ordering = ["-id"]


class Proveedores(models.Model):
    razon_social = models.CharField(max_length=200)
    nombre =  models.CharField(max_length=100)
    email =  models.EmailField(max_length=100, blank=True)
    direccion = models.CharField(max_length=200, blank=True)
    localidad =  models.CharField(max_length=50, blank=True)
    codigo_postal =  models.CharField(max_length=10, blank=True)
    telefono = models.CharField(max_length=10)
    CIF = models.CharField(max_length=50)
    fecha_alta = models.DateField(auto_now_add=True)
    nota = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    def __unicode__(self):
        return self.nombre

    class Meta:
        ordering = ["-id"]


class Clientes(models.Model):

    nombre_completo =  models.CharField(max_length=150)
    email =  models.EmailField(max_length=100, null=True, blank=True)
    password = models.CharField(max_length=200, null=True, blank=True)
    telefono = models.CharField(max_length=10)
    DNI = models.CharField(max_length=50)
    fecha_alta = models.DateField(auto_now_add=True)
    nota = models.TextField(blank=True)
    activo = models.BooleanField(default=True)


    def __unicode__(self):
        return self.nombre_completo


    def authenticated(self, password, email):
        password = make_password(password)
        return password == self.password and self.email == email

    def save(self, *args, **kwargs):
        if self.password != None:
            self.password = make_password(self.password)
        super(Clientes, self).save(*args, **kwargs)

    class Meta:
        ordering = ["-id", 'nombre_completo']
