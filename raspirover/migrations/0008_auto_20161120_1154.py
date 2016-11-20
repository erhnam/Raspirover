# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('raspirover', '0007_auto_20161118_0945'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exploracion',
            name='tiempo',
            field=models.DecimalField(validators=[django.core.validators.MaxValueValidator(10)], max_digits=3, null=True, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='sensor',
            name='nombre',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
