# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-09 23:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cdms', '0006_auto_20170410_0235'),
    ]

    operations = [
        migrations.AddField(
            model_name='officer',
            name='district',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cdms.District'),
        ),
        migrations.AlterField(
            model_name='officer',
            name='admin_type',
            field=models.CharField(blank=True, choices=[(b'A', b'Admin'), (b'S', b'Super Admin'), (b'OC', b'Officer in Charge'), (b'N', b'Normal')], max_length=10, null=True),
        ),
    ]
