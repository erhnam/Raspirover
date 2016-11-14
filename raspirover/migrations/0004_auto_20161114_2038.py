# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('raspirover', '0003_auto_20161114_1027'),
    ]

    operations = [
        migrations.RenameField(
            model_name='exploracion',
            old_name='username',
            new_name='usuario',
        ),
        migrations.RemoveField(
            model_name='exploracion',
            name='sensor',
        ),
        migrations.RemoveField(
            model_name='sensorgas',
            name='enable',
        ),
        migrations.RemoveField(
            model_name='sensorhumedad',
            name='enable',
        ),
        migrations.RemoveField(
            model_name='sensorluz',
            name='enable',
        ),
        migrations.RemoveField(
            model_name='sensortemperatura',
            name='enable',
        ),
        migrations.AddField(
            model_name='exploracion',
            name='sensorGas',
            field=models.ManyToManyField(to='raspirover.SensorGas', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='exploracion',
            name='sensorHunedad',
            field=models.ManyToManyField(to='raspirover.SensorHumedad', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='exploracion',
            name='sensorLuz',
            field=models.ManyToManyField(to='raspirover.SensorLuz', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='exploracion',
            name='sensorTemperatura',
            field=models.ManyToManyField(to='raspirover.SensorTemperatura', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='sensor',
            name='enable',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='sensores',
            name='descripcion',
            field=models.CharField(max_length=140, null=True),
        ),
        migrations.AlterField(
            model_name='exploracion',
            name='descripcion',
            field=models.CharField(max_length=140, null=True),
        ),
    ]
