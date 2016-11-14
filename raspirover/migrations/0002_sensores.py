# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('raspirover', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sensores',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('nombre', models.CharField(max_length=12)),
                ('temperatura', models.BooleanField()),
                ('humedad', models.BooleanField()),
                ('gas', models.BooleanField()),
                ('luz', models.BooleanField()),
                ('camara', models.BooleanField()),
                ('tiempo', models.DecimalField(validators=[django.core.validators.MaxValueValidator(10)], decimal_places=1, null=True, max_digits=3)),
            ],
        ),
    ]
