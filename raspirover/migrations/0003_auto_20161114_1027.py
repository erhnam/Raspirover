# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('raspirover', '0002_sensores'),
    ]

    operations = [
        migrations.AddField(
            model_name='sensorgas',
            name='enable',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='sensorhumedad',
            name='enable',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='sensorluz',
            name='enable',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='sensortemperatura',
            name='enable',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='sensorhumedad',
            name='humedad',
            field=models.FloatField(null=True, validators=[django.core.validators.MinValueValidator(-10), django.core.validators.MaxValueValidator(50)]),
        ),
        migrations.AlterField(
            model_name='sensortemperatura',
            name='temperatura',
            field=models.FloatField(null=True, validators=[django.core.validators.MinValueValidator(-10), django.core.validators.MaxValueValidator(50)]),
        ),
    ]
