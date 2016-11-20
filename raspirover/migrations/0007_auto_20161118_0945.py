# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('raspirover', '0006_auto_20161118_0918'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sensor',
            name='exploraciones',
        ),
        migrations.AddField(
            model_name='exploracion',
            name='sensores',
            field=models.ManyToManyField(to='raspirover.Sensor'),
        ),
    ]
