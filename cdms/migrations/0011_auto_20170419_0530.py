# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-18 23:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cdms', '0010_auto_20170418_0245'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='generaldiary',
            name='stage',
        ),
        migrations.AddField(
            model_name='generaldiary',
            name='is_action_taken',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='generaldiary',
            name='seen_by',
            field=models.CharField(choices=[(b'NS', b'Not Seen'), (b'SUP', b'Seen by Superior officer'), (b'SUB', b'Seen by Subordinate officer')], default='NS', max_length=10),
        ),
    ]
