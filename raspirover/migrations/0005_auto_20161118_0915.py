# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('raspirover', '0004_auto_20161118_0914'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sensores',
            name='tiempo',
            field=models.FloatField(null=True, default=0),
        ),
    ]
