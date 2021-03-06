# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-01-10 19:25
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Abonos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('empleado', models.CharField(max_length=150)),
                ('empleado_id', models.IntegerField(default=-1)),
                ('fecha_salida', models.DateTimeField(auto_now_add=True)),
                ('firma', models.FileField(null=True, upload_to='firmas')),
                ('forma_pago', models.CharField(choices=[('EF', 'Efectivo'), ('TJ', 'Tarjeta')], default='EF', max_length=2)),
            ],
            options={
                'ordering': ['-fecha_salida'],
            },
        ),
        migrations.CreateModel(
            name='Almacenes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(blank=True, max_length=50)),
                ('direccion', models.CharField(max_length=150)),
                ('descripcion', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Categorias',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField(blank=True)),
                ('fecha_creacion', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Clientes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_completo', models.CharField(max_length=150)),
                ('email', models.EmailField(blank=True, max_length=100, null=True)),
                ('password', models.CharField(blank=True, max_length=200, null=True)),
                ('telefono', models.CharField(max_length=10)),
                ('DNI', models.CharField(max_length=50)),
                ('fecha_alta', models.DateField(auto_now_add=True)),
                ('nota', models.TextField(blank=True)),
                ('activo', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['-id', 'nombre_completo'],
            },
        ),
        migrations.CreateModel(
            name='Compras',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vendedor_id', models.IntegerField(null=True)),
                ('fecha_entrada', models.DateTimeField(auto_now_add=True)),
                ('codigo_compra', models.CharField(max_length=150, null=True)),
                ('firma', models.FileField(null=True, upload_to='firmas')),
                ('tipo_compra', models.CharField(choices=[('REBU', 'REBU'), ('ISP', 'ISP')], default='REBU', max_length=4)),
                ('doc_proveedor', models.FileField(default=None, max_length=500, null=True, upload_to='doc_proveedor')),
                ('tipo_vendedor', models.CharField(choices=[('CL', 'Cliente'), ('PV', 'Proveedor'), ('NO', 'No asignado')], default='NO', max_length=2)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='ConfigSite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ISP', models.IntegerField(blank=True, default=21)),
                ('email_policia', models.EmailField(blank=True, max_length=100)),
                ('email_gestoria', models.EmailField(blank=True, max_length=100)),
                ('codigo_compra', models.IntegerField(default=3023, verbose_name='Inicio contador')),
                ('firma_tienda', models.FileField(blank=True, upload_to='config')),
                ('logo_tienda', models.FileField(blank=True, upload_to='config')),
            ],
        ),
        migrations.CreateModel(
            name='Direcciones',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('direccion', models.CharField(blank=True, max_length=200)),
                ('localidad', models.CharField(blank=True, max_length=50)),
                ('codigo_postal', models.CharField(blank=True, max_length=10)),
                ('provincia', models.CharField(blank=True, max_length=50)),
                ('es_principal', models.BooleanField(default=True)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminshop.Clientes')),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='DocumentoTesteo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firma', models.FileField(null=True, upload_to='firmas')),
                ('frimado', models.BooleanField(default=False)),
                ('fecha', models.DateTimeField(auto_now=True)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminshop.Clientes')),
                ('empleado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='DocumentSendGestoria',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField()),
            ],
            options={
                'ordering': ['-fecha'],
            },
        ),
        migrations.CreateModel(
            name='DocumentSendPolice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField()),
            ],
            options={
                'ordering': ['-fecha'],
            },
        ),
        migrations.CreateModel(
            name='Firmas',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_documento', models.CharField(choices=[('CP', 'Compra'), ('FT', 'Factura'), ('RP', 'Reparacion'), ('AB', 'Abono'), ('OS', 'Testeo')], default='CP', max_length=2)),
                ('empleado_id', models.IntegerField()),
                ('documento_id', models.IntegerField()),
                ('fecha', models.DateTimeField(auto_now=True)),
                ('firmado', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-fecha'],
            },
        ),
        migrations.CreateModel(
            name='Garantias',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ns_imei', models.CharField(max_length=100, unique=True, verbose_name='NS o IMEI')),
                ('documento', models.FileField(upload_to='garantias')),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Historial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('detalle', models.CharField(max_length=150)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminshop.Clientes')),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='LineasAbonos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detalle', models.CharField(max_length=150)),
                ('codigo_compra', models.CharField(max_length=150)),
                ('ns_imei', models.CharField(max_length=150)),
                ('descuento', models.DecimalField(decimal_places=2, max_digits=5)),
                ('can', models.IntegerField()),
                ('p_unidad', models.DecimalField(decimal_places=2, max_digits=10)),
                ('abono', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminshop.Abonos')),
            ],
        ),
        migrations.CreateModel(
            name='LineasPresupuesto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detalle', models.CharField(max_length=150)),
                ('codigo', models.CharField(max_length=150)),
                ('can', models.IntegerField()),
                ('precio', models.DecimalField(decimal_places=2, max_digits=10)),
                ('descuento', models.DecimalField(decimal_places=2, max_digits=6)),
            ],
        ),
        migrations.CreateModel(
            name='LineasVentas',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detalle', models.CharField(max_length=150)),
                ('codigo_compra', models.CharField(max_length=150)),
                ('ns_imei', models.CharField(max_length=150)),
                ('descuento', models.DecimalField(decimal_places=2, max_digits=6)),
                ('can', models.IntegerField()),
                ('p_unidad', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='ListaTesteo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField(blank=True)),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminshop.Categorias')),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Marcas',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(blank=True, max_length=50)),
                ('logo', models.FileField(upload_to='logo_marcas')),
                ('descripcion', models.TextField(blank=True)),
                ('fecha_creacion', models.DateTimeField(auto_now=True)),
                ('categorias', models.ManyToManyField(to='adminshop.Categorias')),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Modelos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(blank=True, max_length=50)),
                ('precio_usado', models.DecimalField(decimal_places=2, max_digits=9, null=True, verbose_name='Precio usado')),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminshop.Categorias')),
                ('marca', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminshop.Marcas')),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='NotasReparacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detalle', models.CharField(max_length=150)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Presupuesto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('firma', models.FileField(null=True, upload_to='firmas')),
                ('notas_cliente', models.TextField(blank=True)),
                ('notas_tecnico', models.TextField(blank=True)),
                ('entrega', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('estado', models.CharField(choices=[('FT', 'Facturado'), ('NO', 'No facturado')], default='NO', max_length=2)),
                ('cliente', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='adminshop.Clientes')),
                ('empleado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Productos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color', models.CharField(max_length=50, null=True)),
                ('ns_imei', models.CharField(max_length=50, unique=True, verbose_name='NS o IMEI')),
                ('precio_venta', models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True, verbose_name='Precio de venta')),
                ('precio_compra', models.DecimalField(decimal_places=2, max_digits=9, null=True, verbose_name='Precio compra')),
                ('descuento', models.IntegerField(blank=True, default=0, null=True)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('es_unico', models.BooleanField(default=True)),
                ('detalle', models.CharField(max_length=150, null=True)),
                ('estado', models.CharField(choices=[('ST', 'En stock'), ('VT', 'En venta'), ('OL', 'En venta online'), ('RP', 'En reparacion'), ('OK', 'Reparado'), ('OS', 'Testeo'), ('PS', 'Presupuestar'), ('PD', 'Presupuestado'), ('TD', 'Testeado'), ('CT', 'Cliente'), ('VD', 'Vendido')], default='VT', max_length=2)),
                ('localizacion', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, to='adminshop.Almacenes')),
                ('modelo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='adminshop.Modelos')),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Proveedores',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('razon_social', models.CharField(max_length=200)),
                ('nombre', models.CharField(max_length=100)),
                ('email', models.EmailField(blank=True, max_length=100)),
                ('direccion', models.CharField(blank=True, max_length=200)),
                ('localidad', models.CharField(blank=True, max_length=50)),
                ('codigo_postal', models.CharField(blank=True, max_length=10)),
                ('telefono', models.CharField(max_length=10)),
                ('CIF', models.CharField(max_length=50)),
                ('fecha_alta', models.DateField(auto_now_add=True)),
                ('nota', models.TextField(blank=True)),
                ('activo', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Reparaciones',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detalle', models.CharField(max_length=150)),
                ('codigo', models.CharField(max_length=150, unique=True)),
                ('precio', models.DecimalField(decimal_places=2, max_digits=10)),
                ('marca', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='adminshop.Marcas')),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Testeo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nota', models.CharField(max_length=150)),
                ('estado', models.CharField(choices=[('NO', 'No Realizado'), ('OK', 'Aprobado'), ('ER', 'Suspenso')], default='NO', max_length=2)),
                ('descripcion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminshop.ListaTesteo')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminshop.Productos')),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Tipos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(blank=True, max_length=50)),
                ('descripcion', models.TextField(blank=True)),
                ('incremento', models.DecimalField(decimal_places=2, max_digits=9, null=True)),
            ],
            options={
                'ordering': ['-incremento'],
            },
        ),
        migrations.CreateModel(
            name='Ventas',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('empleado', models.CharField(max_length=150)),
                ('empleado_id', models.IntegerField(default=-1)),
                ('fecha_salida', models.DateTimeField(auto_now_add=True)),
                ('firma', models.FileField(null=True, upload_to='firmas')),
                ('entrega', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('forma_pago', models.CharField(choices=[('EF', 'Efectivo'), ('TJ', 'Tarjeta')], default='EF', max_length=2)),
                ('cliente', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='adminshop.Clientes')),
            ],
            options={
                'ordering': ['-fecha_salida'],
            },
        ),
        migrations.AddField(
            model_name='productos',
            name='tipo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='adminshop.Tipos'),
        ),
        migrations.AddField(
            model_name='presupuesto',
            name='factura',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='adminshop.Ventas'),
        ),
        migrations.AddField(
            model_name='presupuesto',
            name='producto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminshop.Productos'),
        ),
        migrations.AddField(
            model_name='notasreparacion',
            name='presupuesto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminshop.Presupuesto'),
        ),
        migrations.AddField(
            model_name='notasreparacion',
            name='usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='modelos',
            name='tipos_aceptados',
            field=models.ManyToManyField(to='adminshop.Tipos'),
        ),
        migrations.AddField(
            model_name='lineasventas',
            name='venta',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminshop.Ventas'),
        ),
        migrations.AddField(
            model_name='lineaspresupuesto',
            name='presupuesto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminshop.Presupuesto'),
        ),
        migrations.AddField(
            model_name='historial',
            name='producto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminshop.Productos'),
        ),
        migrations.AddField(
            model_name='historial',
            name='usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='documentotesteo',
            name='producto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminshop.Productos'),
        ),
        migrations.AddField(
            model_name='compras',
            name='producto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminshop.Productos'),
        ),
        migrations.AddField(
            model_name='compras',
            name='usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='abonos',
            name='cliente',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='adminshop.Clientes'),
        ),
        migrations.AddField(
            model_name='abonos',
            name='factura',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminshop.Ventas'),
        ),
    ]
