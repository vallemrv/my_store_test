# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   26-Aug-2017
# @Email:  valle.mrv@gmail.com
# @Filename: models.py
# @Last modified by:   valle
# @Last modified time: 24-Mar-2018
# @License: Apache license vesion 2.0


from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
import os


ESTADO_CHOICES = (
    ('ST', 'En stock'),
    ('VT', 'En venta'),
    ('OL', 'En venta online'),
    ('RP', 'En reparacion'),
    ('OK', 'Reparado'),
    ('OS', 'Testeo'),
    ('PS', 'Presupuestar'),
    ('PD', 'Presupuestado'),
    ('TD', "Testeado"),
    ('CT', "Cliente"),
    ('VD', 'Vendido'),
)

class Categorias(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.nombre

    class Meta:
        ordering = ["-id"]

class Tipos(models.Model):
    nombre = models.CharField(max_length=50, blank=True)
    descripcion = models.TextField(blank=True)
    incremento = models.DecimalField(max_digits=9, decimal_places=2, null=True)

    def __unicode__(self):
        return self.nombre

    class Meta:
        ordering = ["-incremento"]

class Marcas(models.Model):
    nombre = models.CharField(max_length=50, blank=True)
    logo = models.FileField(upload_to='logo_marcas')
    descripcion = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now=True)
    categorias = models.ManyToManyField("Categorias")

    def __unicode__(self):
        return self.nombre

    class Meta:
        ordering = ["-id"]

class Modelos(models.Model):
    categoria = models.ForeignKey('Categorias', on_delete=models.CASCADE)
    marca = models.ForeignKey('Marcas', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50, blank=True)
    precio_usado = models.DecimalField("Precio usado", max_digits=9, decimal_places=2, null=True)
    tipos_aceptados = models.ManyToManyField("Tipos")


    def __unicode__(self):
        return self.nombre

    class Meta:
        ordering = ["-id"]

class Almacenes(models.Model):
    nombre = models.CharField(max_length=50, blank=True)
    direccion = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    def __unicode__(self):
        return self.nombre

    class Meta:
        ordering = ["-id"]

class Garantias(models.Model):
    documento = models.FileField(upload_to='garantias')

    def __unicode__(self):
        return os.path.basename(self.documento.name).replace(".pdf", "")

    class Meta:
        ordering = ["-id"]

class Productos(models.Model):
    tipo = models.ForeignKey('Tipos', on_delete=models.SET_NULL, null=True, blank=True)
    modelo = models.ForeignKey('Modelos', on_delete=models.SET_NULL, null=True, blank=True)
    color = models.CharField(max_length=50, null=True)
    localizacion = models.ForeignKey('Almacenes', on_delete=models.SET_DEFAULT, null=True, default=1)
    ns_imei = models.CharField("NS o IMEI", unique=True, max_length=50)
    precio_venta = models.DecimalField("Precio de venta", max_digits=9, decimal_places=2, null=True, blank=True)
    precio_compra = models.DecimalField("Precio compra", max_digits=9, decimal_places=2, null=True)
    descuento = models.IntegerField(default=0, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    es_unico = models.BooleanField(default=True, blank=True)
    detalle =  models.CharField(max_length=150, null=True)
    estado = models.CharField(
        max_length=2,
        choices=ESTADO_CHOICES,
        default="VT",
    )

    def get_descripcion_tipo(self):
        if self.es_unico and self.tipo != None and self.modelo != None:
            return unicode(self.tipo.descripcion)
        elif self.es_unico and self.tipo != None and self.modelo == None:
            return unicode(self.tipo.descripcion)
        elif not self.es_unico and self.tipo != None and self.modelo != None:
            return unicode(self.tipo.descripcion)
        else:
            return ""

    def get_detalle_factura(self):
        if self.es_unico and self.tipo != None and self.modelo != None:
            return unicode(self.modelo)+", TIPO: "+unicode(self.tipo.descripcion)+", IMEI: "+unicode(self.ns_imei)
        elif self.tipo != None and self.modelo != None:
            return unicode(self.modelo)+", TIPO: "+unicode(self.tipo.descripcion)+", IMEI: "+unicode(self.ns_imei)
        elif self.modelo != None:
            return unicode(self.modelo)+", IMEI: "+unicode(self.ns_imei)
        elif self.es_unico and self.modelo != None and self.tipo == None:
            return unicode(self.modelo)+ ", Ns o IMEI: "+unicode(self.ns_imei)
        elif self.detalle != None:
            return unicode(self.detalle)+ ", Ns o IMEI: "+self.ns_imei
        else:
            return "Nuevo producto"+ ", Ns o IMEI: "+self.ns_imei


    def set_vendido(self):
        if self.es_unico:
            self.estado = "VD"
        else:
            self.estado = "VT"

    def __unicode__(self):
        if self.es_unico and self.modelo != None:
            return self.modelo.nombre
        elif self.modelo != None:
            return self.modelo.nombre
        else:
            return unicode(self.detalle)

    class Meta:
        ordering = ["-id"]
