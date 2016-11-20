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
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('fecha', models.DateTimeField(null=True, auto_now_add=True)),
                ('descripcion', models.CharField(max_length=140, null=True)),
                ('tiempo', models.DecimalField(decimal_places=1, null=True, max_digits=3, validators=[django.core.validators.MaxValueValidator(10)])),
            ],
        ),
        migrations.CreateModel(
            name='Sensor',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('descripcion', models.CharField(max_length=140)),
                ('fecha', models.DateTimeField(null=True, auto_now_add=True)),
                ('enable', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Sensores',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('nombre', models.CharField(max_length=12)),
                ('temperatura', models.BooleanField()),
                ('humedad', models.BooleanField()),
                ('gas', models.BooleanField()),
                ('luz', models.BooleanField()),
                ('camara', models.BooleanField()),
                ('descripcion', models.CharField(max_length=140, null=True)),
                ('tiempo', models.DecimalField(decimal_places=1, null=True, max_digits=3, validators=[django.core.validators.MaxValueValidator(10)])),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('user', models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('photo', models.ImageField(blank=True, upload_to='profiles', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='sensorGas',
            fields=[
                ('sensor_ptr', models.OneToOneField(primary_key=True, serialize=False, to='raspirover.Sensor', auto_created=True, parent_link=True)),
                ('gas', models.IntegerField(null=True)),
            ],
            bases=('raspirover.sensor',),
        ),
        migrations.CreateModel(
            name='sensorHumedad',
            fields=[
                ('sensor_ptr', models.OneToOneField(primary_key=True, serialize=False, to='raspirover.Sensor', auto_created=True, parent_link=True)),
                ('humedad', models.FloatField(null=True, validators=[django.core.validators.MinValueValidator(-10), django.core.validators.MaxValueValidator(50)])),
            ],
            bases=('raspirover.sensor',),
        ),
        migrations.CreateModel(
            name='sensorLuz',
            fields=[
                ('sensor_ptr', models.OneToOneField(primary_key=True, serialize=False, to='raspirover.Sensor', auto_created=True, parent_link=True)),
                ('luz', models.IntegerField(null=True)),
            ],
            bases=('raspirover.sensor',),
        ),
        migrations.CreateModel(
            name='sensorTemperatura',
            fields=[
                ('sensor_ptr', models.OneToOneField(primary_key=True, serialize=False, to='raspirover.Sensor', auto_created=True, parent_link=True)),
                ('temperatura', models.FloatField(null=True, validators=[django.core.validators.MinValueValidator(-10), django.core.validators.MaxValueValidator(50)])),
            ],
            bases=('raspirover.sensor',),
        ),
        migrations.AddField(
            model_name='sensor',
            name='exploraciones',
            field=models.ManyToManyField(related_name='sh', to='raspirover.Exploracion'),
        ),
        migrations.AddField(
            model_name='exploracion',
            name='usuario',
            field=models.ForeignKey(to='raspirover.UserProfile'),
        ),
    ]
