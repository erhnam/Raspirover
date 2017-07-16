# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-15 11:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('raspirover', '0002_auto_20170714_0932'),
    ]

    operations = [
        migrations.CreateModel(
            name='sensorGps',
            fields=[
                ('sensor_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='raspirover.Sensor')),
                ('lat', models.FloatField(default=0.0, null=True)),
                ('lon', models.FloatField(default=0.0, null=True)),
            ],
            options={
                'db_table': 'SensorGps',
            },
            bases=('raspirover.sensor',),
        ),
    ]
