# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('raspirover', '0008_auto_20161120_1154'),
    ]

    operations = [
        migrations.AddField(
            model_name='sensortemperatura',
            name='date',
            field=models.DateTimeField(null=True, auto_now_add=True),
        ),
    ]
