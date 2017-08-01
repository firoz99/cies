# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-11 11:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cdms', '0007_auto_20170410_0545'),
    ]

    operations = [
        migrations.AddField(
            model_name='officer',
            name='officer_type',
            field=models.CharField(blank=True, choices=[(b'A', b'Admin'), (b'T', b'Thana'), (b'R', b'Reserve')], max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='officer',
            name='position',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]