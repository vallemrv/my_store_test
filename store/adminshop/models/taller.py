# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   26-Aug-2017
# @Email:  valle.mrv@gmail.com
# @Filename: models.py
# @Last modified by:   valle
# @Last modified time: 16-Dec-2017
# @License: Apache license vesion 2.0


from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

ESTADO_CHOICES_TESTEO = (
    ('NO', 'No Realizado'),
    ('OK', 'Aprobado'),
    ('ER', 'Suspenso'),
)

CHOICES_ESTADO_PRESUPUESTO = (
    ('FT', 'Facturado'),
    ('NO', 'No facturado'),
)

class ListaTesteo(models.Model):
    categoria = models.ForeignKey('Categorias', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    def __unicode__(self):
        return self.nombre

    class Meta:
        ordering = ["-id"]

class Testeo(models.Model):
    descripcion = models.ForeignKey("ListaTesteo", on_delete=models.CASCADE )
    producto = models.ForeignKey("Productos",  on_delete=models.CASCADE )
    nota = models.CharField(max_length=150)
    estado = models.CharField(
        max_length=2,
        choices=ESTADO_CHOICES_TESTEO,
        default="NO",
    )


    def __unicode__(self):
        return self.get_estado_display()

    class Meta:
        ordering = ["-id"]



class Presupuesto(models.Model):
    cliente = models.ForeignKey("Clientes", on_delete=models.SET_NULL, null=True)
    factura = models.ForeignKey("Ventas", on_delete=models.SET_NULL, null=True)
    empleado = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    firma = models.FileField(upload_to='firmas', null=True)
    notas_cliente = models.TextField(blank=True)
    notas_tecnico = models.TextField(blank=True)
    producto = models.ForeignKey("Productos", on_delete=models.CASCADE)
    entrega = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(
        max_length=2,
        choices=CHOICES_ESTADO_PRESUPUESTO,
        default="NO",
    )

    class Meta:
        ordering = ["-id"]


class LineasPresupuesto(models.Model):
    presupuesto = models.ForeignKey("Presupuesto", on_delete=models.CASCADE)
    detalle = models.CharField(max_length=150)
    codigo = models.CharField(max_length=150)
    can = models.IntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=6, decimal_places=2)


class Reparaciones(models.Model):
    marca = models.ForeignKey("Marcas", on_delete=models.SET_NULL, null=True)
    detalle = models.CharField(max_length=150)
    codigo = models.CharField(max_length=150, unique=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["-id"]


class NotasReparacion(models.Model):
    presupuesto = models.ForeignKey("Presupuesto", on_delete=models.CASCADE)
    detalle = models.CharField(max_length=150)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-id"]
