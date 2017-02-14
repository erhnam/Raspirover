# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('raspirover', '0003_auto_20161219_1640'),
    ]

    operations = [
        migrations.AddField(
            model_name='exploracion',
            name='video',
            field=models.CharField(max_length=250, null=True),
        ),
    ]
