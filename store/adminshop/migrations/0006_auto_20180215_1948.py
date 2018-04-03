# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-15 18:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminshop', '0005_auto_20180202_1902'),
    ]

    operations = [
        migrations.AlterField(
            model_name='abonos',
            name='forma_pago',
            field=models.CharField(choices=[('EF', 'Efectivo'), ('TJ', 'Tarjeta'), ('TB', 'Transferencia bancaria'), ('PY', 'Paypal'), ('CR', 'Contrarembolso')], default='EF', max_length=2),
        ),
        migrations.AlterField(
            model_name='ventas',
            name='forma_pago',
            field=models.CharField(choices=[('EF', 'Efectivo'), ('TJ', 'Tarjeta'), ('TB', 'Transferencia bancaria'), ('PY', 'Paypal'), ('CR', 'Contrarembolso')], default='EF', max_length=2),
        ),
    ]
