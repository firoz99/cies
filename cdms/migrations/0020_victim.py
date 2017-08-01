# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-22 20:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cdms', '0019_auto_20170420_0955'),
    ]

    operations = [
        migrations.CreateModel(
            name='Victim',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('father_name', models.CharField(blank=True, max_length=100, verbose_name="Father's Name")),
                ('mother_name', models.CharField(blank=True, max_length=100, verbose_name="Mother's Name")),
                ('present_address', models.CharField(blank=True, max_length=300)),
                ('permanent_address', models.CharField(blank=True, max_length=300)),
                ('national_id', models.CharField(blank=True, max_length=100)),
                ('mobile', models.CharField(blank=True, max_length=50)),
                ('case', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cdms.Case')),
            ],
        ),
    ]
