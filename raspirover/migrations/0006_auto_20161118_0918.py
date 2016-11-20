# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('raspirover', '0005_auto_20161118_0915'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exploracion',
            name='tiempo',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='sensor',
            name='exploraciones',
            field=models.ManyToManyField(to='raspirover.Exploracion'),
        ),
    ]
