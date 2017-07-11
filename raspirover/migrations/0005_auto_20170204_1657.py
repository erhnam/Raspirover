# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('raspirover', '0004_exploracion_video'),
    ]

    operations = [
        migrations.CreateModel(
            name='sensorCamara',
            fields=[
                ('sensor_ptr', models.OneToOneField(auto_created=True, primary_key=True, serialize=False, to='raspirover.Sensor', parent_link=True)),
                ('video', models.CharField(max_length=250, null=True)),
            ],
            options={
                'db_table': 'SensorCamara',
            },
            bases=('raspirover.sensor',),
        ),
        migrations.RemoveField(
            model_name='exploracion',
            name='video',
        ),
    ]
