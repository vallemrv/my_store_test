# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-01-10 19:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminshop', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='compras',
            name='enviar_policia',
            field=models.BooleanField(default=True, verbose_name='Enviar a la policia'),
        ),
    ]
