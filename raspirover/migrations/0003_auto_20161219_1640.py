# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('raspirover', '0002_auto_20161219_1637'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sensorgas',
            name='gas',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='sensorluz',
            name='luz',
            field=models.IntegerField(null=True),
        ),
    ]
