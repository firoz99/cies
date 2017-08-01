# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-23 23:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cdms', '0022_auto_20170424_0453'),
    ]

    operations = [
        migrations.RenameField(
            model_name='criminal_fir_list',
            old_name='fir',
            new_name='fir_number',
        ),
        migrations.AddField(
            model_name='criminal_fir_list',
            name='fir_id',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='case',
            name='reason',
            field=models.CharField(blank=True, max_length=300, null=True, verbose_name='Why late to file a FIR'),
        ),
    ]