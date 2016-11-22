# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Exploracion',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('nombre', models.CharField(max_length=150, unique=True)),
                ('fecha', models.DateTimeField(null=True, auto_now_add=True)),
                ('descripcion', models.CharField(null=True, max_length=140)),
                ('tiempo', models.DecimalField(decimal_places=1, null=True, validators=[django.core.validators.MaxValueValidator(10)], max_digits=3)),
            ],
        ),
        migrations.CreateModel(
            name='Sensor',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('tipo', models.CharField(null=True, max_length=20)),
                ('descripcion', models.CharField(max_length=140)),
                ('fecha', models.DateTimeField(null=True, auto_now_add=True)),
                ('enable', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Sensores',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('nombre', models.CharField(max_length=12)),
                ('temperatura', models.BooleanField()),
                ('humedad', models.BooleanField()),
                ('gas', models.BooleanField()),
                ('luz', models.BooleanField()),
                ('camara', models.BooleanField()),
                ('descripcion', models.CharField(null=True, max_length=140)),
                ('tiempo', models.FloatField(null=True, default=0)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, primary_key=True, serialize=False)),
                ('photo', models.ImageField(upload_to='profiles', null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='sensorGas',
            fields=[
                ('sensor_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='raspirover.Sensor')),
                ('gas', models.IntegerField(default=False)),
            ],
            bases=('raspirover.sensor',),
        ),
        migrations.CreateModel(
            name='sensorHumedad',
            fields=[
                ('sensor_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='raspirover.Sensor')),
                ('humedad', models.DecimalField(decimal_places=1, null=True, validators=[django.core.validators.MinValueValidator(-10), django.core.validators.MaxValueValidator(50)], max_digits=3)),
            ],
            bases=('raspirover.sensor',),
        ),
        migrations.CreateModel(
            name='sensorLuz',
            fields=[
                ('sensor_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='raspirover.Sensor')),
                ('luz', models.BooleanField(default=False)),
            ],
            bases=('raspirover.sensor',),
        ),
        migrations.CreateModel(
            name='sensorTemperatura',
            fields=[
                ('sensor_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='raspirover.Sensor')),
                ('temperatura', models.DecimalField(decimal_places=1, null=True, validators=[django.core.validators.MinValueValidator(-10), django.core.validators.MaxValueValidator(50)], max_digits=3)),
            ],
            bases=('raspirover.sensor',),
        ),
        migrations.AddField(
            model_name='exploracion',
            name='sensores',
            field=models.ManyToManyField(to='raspirover.Sensor'),
        ),
        migrations.AddField(
            model_name='exploracion',
            name='usuario',
            field=models.ForeignKey(null=True, to='raspirover.UserProfile'),
        ),
    ]
