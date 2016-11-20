# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('raspirover', '0002_auto_20161118_0908'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exploracion',
            name='usuario',
            field=models.ForeignKey(to='raspirover.UserProfile', null=True),
        ),
    ]
