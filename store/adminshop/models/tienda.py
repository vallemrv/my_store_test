# -*- coding: utf-8 -*-

# @Author: Manuel Rodriguez <valle>
# @Date:   28-Aug-2017
# @Email:  valle.mrv@gmail.com
# @Filename: models.py
# @Last modified by:   valle
# @Last modified time: 15-Feb-2018
# @License: Apache license vesion 2.0


from __future__ import unicode_literals
from django.db.models import Q
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from adminshop.models import (Clientes, Direcciones, Proveedores,
                              Productos, Presupuesto)

# Create your models here.
CHOICES_TIPO_PAGO = (
    ('EF', 'Efectivo'),
    ('TJ', 'Tarjeta'),
    ('TB', 'Transferencia bancaria'),
    ('PY', 'Paypal'),
    ('CR', 'Contrarembolso'),
)

CHOICES_TIPO_VENDEDOR = (
    ('CL', 'Cliente'),
    ('PV', 'Proveedor'),
    ('NO', 'No asignado')
)

CHOICES_TIPO_DOC = (
    ('CP', 'Compra'),
    ('FT', 'Factura'),
    ('RP', 'Reparacion'),
    ('AB', 'Abono'),
    ('OS', 'Testeo')
)


class DocumentSendPolice(models.Model):
    fecha_creado = models.DateTimeField(auto_now_add=True)
    enviado = models.BooleanField(default=False)
    intervalo = models.CharField(max_length=25)

    class Meta:
        ordering = ["-fecha_creado"]

class DocumentSendGestoria(models.Model):
    fecha_creado = models.DateTimeField(auto_now_add=True)
    enviado = models.BooleanField(default=False)
    intervalo = models.CharField(max_length=25)

    class Meta:
        ordering = ["-fecha_creado"]


class DocumentoTesteo(models.Model):
    cliente = models.ForeignKey("clientes", on_delete=models.CASCADE )
    producto = models.ForeignKey("Productos",  on_delete=models.CASCADE )
    empleado = models.ForeignKey(User,  on_delete=models.CASCADE )
    firma = models.FileField(upload_to='firmas', null=True)
    frimado = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return str(self.cliente)

    class Meta:
        ordering = ["-id"]

class ConfigSite(models.Model):
    ISP = models.IntegerField(blank=True, default=21)
    email_policia = models.EmailField(max_length=100, blank=True)
    email_gestoria = models.EmailField(max_length=100, blank=True)
    codigo_compra = models.IntegerField("Inicio contador", default=3023)
    firma_tienda = models.FileField(upload_to='config', blank=True)
    logo_tienda = models.FileField(upload_to='config', blank=True)


class Compras(models.Model):
    vendedor_id = models.IntegerField(null=True)
    producto = models.ForeignKey("Productos", on_delete=models.CASCADE)
    usuario  = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_entrada = models.DateTimeField(auto_now_add=True)
    codigo_compra = models.CharField(max_length=150, null=True)
    firma = models.FileField(upload_to='firmas', null=True)
    tipo_compra = models.CharField(max_length=4, default="REBU", choices=[("REBU","REBU"), ("ISP","ISP")])
    doc_proveedor = models.FileField(upload_to='doc_proveedor', null=True, default=None, max_length=500)
    enviar_policia = models.BooleanField("Enviar a la policia", blank=True,  default=True)
    tipo_vendedor = models.CharField(
        max_length=2,
        choices=CHOICES_TIPO_VENDEDOR,
        default="NO",
    )

    def set_vendedor(self, vendedor):
        if vendedor != None:
            self.vendedor_id = vendedor.id
            if type(vendedor) == Clientes:
                self.tipo_vendedor = "CL"
            else:
                self.tipo_vendedor = "PV"
        else:
            self.tipo_vendedor = "NO"

    def get_vendedor(self):
        if self.tipo_vendedor == "CL":
            clientes = Clientes.objects.filter(Q(pk=self.vendedor_id))
            if len(clientes) > 0:
                cliente = clientes[0]
                vendedor = {}
                vendedor["DNI"] = cliente.DNI
                vendedor["nombre"] = cliente.nombre_completo
                direcciones = Direcciones.objects.filter(cliente_id=self.vendedor_id)
                if len(direcciones) > 0:
                    direccion = direcciones[0]
                else:
                    direccion = ""
                vendedor["direccion"] = direccion
                vendedor["telefono"] = cliente.telefono
                vendedor["email"] = cliente.email
                vendedor["id"] = cliente.id
                return vendedor
            else:
                return {"DNI":"", "nombre":"", 'direccion':"", 'telefono':'', "email": "", "id":-1}
        elif self.tipo_vendedor == "PV":
            ps = Proveedores.objects.filter(Q(pk=self.vendedor_id))
            if len(ps) > 0:
                p = ps[0]
                vendedor = {}
                vendedor["DNI"] = p.CIF
                vendedor["nombre"] = p.razon_social
                vendedor["direccion"] = p.direccion
                vendedor["telefono"] = p.telefono
                vendedor["email"] = p.email
                vendedor["id"] = p.id
                return vendedor
            else:
                return {"DNI":"", "nombre":"", 'direccion':"", 'telefono':'', "email": "", "id":-1}
        else:
            return {"DNI":"", "nombre":"", 'direccion':"", 'telefono':'', "email": "", "id":-1}

    def save(self, *args, **kwargs):
        super(Compras, self).save()
        if self.codigo_compra == None:
            self.codigo_compra = ConfigSite.objects.all()[0].codigo_compra+self.pk
        super(Compras, self).save()

    class Meta:
        ordering= ["-id"]


class Ventas(models.Model):
    cliente = models.ForeignKey("Clientes", on_delete=models.SET_NULL, null=True)
    empleado = models.CharField(max_length=150)
    empleado_id = models.IntegerField(default=-1)
    fecha_salida= models.DateTimeField(auto_now_add=True)
    firma = models.FileField(upload_to='firmas', null=True)
    entrega = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    forma_pago = models.CharField(
        max_length=2,
        choices=CHOICES_TIPO_PAGO,
        default="EF",
    )

    def get_user(self):
        empleados = User.objects.filter(pk=self.empleado_id)
        if len(empleados) > 0:
            return empleados[0]
        else:
            return User()

    class Meta:
        ordering = ['-fecha_salida']

class LineasVentas(models.Model):
    venta = models.ForeignKey("Ventas", on_delete=models.CASCADE)
    detalle = models.CharField(max_length=150)
    codigo_compra = models.CharField(max_length=150)
    ns_imei = models.CharField(max_length=150)
    descuento = models.DecimalField(max_digits=6, decimal_places=2)
    can = models.IntegerField()
    p_unidad = models.DecimalField(max_digits=10, decimal_places=2)



class Abonos(models.Model):
    factura = models.ForeignKey("Ventas", on_delete=models.CASCADE)
    cliente = models.ForeignKey("Clientes", on_delete=models.SET_NULL, null=True)
    empleado = models.CharField(max_length=150)
    empleado_id = models.IntegerField(default=-1)
    fecha_salida= models.DateTimeField(auto_now_add=True)
    firma = models.FileField(upload_to='firmas', null=True)
    forma_pago = models.CharField(
        max_length=2,
        choices=CHOICES_TIPO_PAGO,
        default="EF",
    )

    def get_user(self):
        empleados = User.objects.filter(pk=self.empleado_id)
        if len(empleados) > 0:
            return empleados[0]
        else:
            return User()

    class Meta:
        ordering = ['-fecha_salida']

class LineasAbonos(models.Model):
    abono = models.ForeignKey("Abonos", on_delete=models.CASCADE)
    detalle = models.CharField(max_length=150)
    codigo_compra = models.CharField(max_length=150)
    ns_imei = models.CharField(max_length=150)
    descuento = models.DecimalField(max_digits=5, decimal_places=2)
    can = models.IntegerField()
    p_unidad = models.DecimalField(max_digits=10, decimal_places=2)




class Historial(models.Model):
    cliente = models.ForeignKey("Clientes", on_delete=models.CASCADE)
    producto = models.ForeignKey("Productos", on_delete=models.CASCADE)
    usuario  = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    detalle = models.CharField(max_length=150)

    def __unicode__(self):
        return self.detalle

    class Meta:
        ordering = ["-id"]


class Firmas(models.Model):
    tipo_documento = models.CharField(
        max_length=2,
        choices=CHOICES_TIPO_DOC,
        default="CP",
    )
    empleado_id = models.IntegerField()
    documento_id = models.IntegerField()
    fecha = models.DateTimeField(auto_now=True)
    firmado = models.BooleanField(default=False)

    def get_user(self):
        empleados = User.objects.filter(pk=self.empleado_id)
        if len(empleados) > 0:
            return empleados[0]
        else:
            return User()

    def get_nombre_cliente(self):
        if self.tipo_documento == "CP":
            try:
                compra = Compras.objects.get(pk=self.documento_id)
                vendedor = compra.get_vendedor()
            except:
                vendedor = { "nombre": "Documento borrado"}

            return vendedor["nombre"]
        elif self.tipo_documento == "RP":
            try:
                p = Presupuesto.objects.get(pk=self.documento_id)
                cliente = p.cliente.nombre_completo
            except:
                cliente  = "Documento borrado"
            return cliente

        elif self.tipo_documento == "OS":
            p = DocumentoTesteo.objects.get(pk=self.documento_id)
            cliente = p.cliente
            return cliente.nombre_completo

    def get_ns_imei(self):
        if self.tipo_documento == "CP":
            try:
                compra = Compras.objects.get(pk=self.documento_id)
                return compra.producto.ns_imei
            except:
                return "Documento borrado"
        elif self.tipo_documento == "RP":
            try:
                p = Presupuesto.objects.get(pk=self.documento_id)
                ns_imei = p.producto.ns_imei
            except:
                ns_imei  = "Documento borrado"
            return ns_imei

        elif self.tipo_documento == "OS":
            p = DocumentoTesteo.objects.get(pk=self.documento_id)
            return p.producto.ns_imei

    def get_producto_pk(self):
        if self.tipo_documento == "CP":
            try:
                compra = Compras.objects.get(pk=self.documento_id)
                return compra.producto.id
            except:
                return 0
        elif self.tipo_documento == "RP":
            try:
                p = Presupuesto.objects.get(pk=self.documento_id)
                ns_imei = p.producto.id
            except:
                ns_imei  = 0
            return ns_imei

        elif self.tipo_documento == "OS":
            p = DocumentoTesteo.objects.get(pk=self.documento_id)
            return p.producto.pk


    def get_documento(self):
        if self.tipo_documento == "CP":
            compra = Compras.objects.get(pk=self.documento_id)
            vendedor = compra.get_vendedor()
            datos_send= {
                "pk": compra.pk,
                "id_producto": compra.producto.pk,
                'nombre': vendedor["nombre"],
                "DNI": vendedor["DNI"],
                "ns_imei": compra.producto.ns_imei,
                "precio_compra": str(compra.producto.precio_compra),
            }
            return "tienda/sign/sign_compras.html", datos_send
        elif self.tipo_documento == "RP":
            try:
                p = Presupuesto.objects.get(pk=self.documento_id)
                cliente = p.cliente
                datos_send= {
                    "pk": p.pk,
                    "id_producto": p.producto.pk,
                    'nombre': cliente.nombre_completo,
                    "DNI": cliente.DNI,
                    "ns_imei": p.producto.ns_imei,
                }
                return "tienda/sign/sign_reparacion.html", datos_send
            except:
                self.delete()
                return None, None
        elif self.tipo_documento == "OS":
            try:
                p = DocumentoTesteo.objects.get(pk=self.documento_id)
                cliente = p.cliente
                datos_send= {
                    "pk": p.pk,
                    "id_producto": p.producto.pk,
                    'nombre': cliente.nombre_completo,
                    "DNI": cliente.DNI,
                    "ns_imei": p.producto.ns_imei,
                }
                return "tienda/sign/sign_testeo.html", datos_send
            except:
                self.delete()
                return None, None

    class Meta:
        ordering = ["-fecha"]
