# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Exploracion',
            fields=[
                ('id_exploracion', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=50)),
                ('fecha', models.DateTimeField(auto_now_add=True, null=True)),
                ('descripcion', models.CharField(max_length=140)),
                ('tiempo', models.DecimalField(validators=[django.core.validators.MaxValueValidator(10)], decimal_places=1, max_digits=3, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Sensor',
            fields=[
                ('id_sensor', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=50)),
                ('descripcion', models.CharField(max_length=140)),
                ('fecha', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('user', models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL, related_name='user_profile')),
                ('photo', models.ImageField(upload_to='profiles', blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SensorGas',
            fields=[
                ('sensor_ptr', models.OneToOneField(primary_key=True, auto_created=True, serialize=False, parent_link=True, to='raspirover.Sensor')),
                ('gas', models.IntegerField(null=True)),
            ],
            bases=('raspirover.sensor',),
        ),
        migrations.CreateModel(
            name='SensorHumedad',
            fields=[
                ('sensor_ptr', models.OneToOneField(primary_key=True, auto_created=True, serialize=False, parent_link=True, to='raspirover.Sensor')),
                ('humedad', models.FloatField(null=True)),
            ],
            bases=('raspirover.sensor',),
        ),
        migrations.CreateModel(
            name='SensorLuz',
            fields=[
                ('sensor_ptr', models.OneToOneField(primary_key=True, auto_created=True, serialize=False, parent_link=True, to='raspirover.Sensor')),
                ('luz', models.IntegerField(null=True)),
            ],
            bases=('raspirover.sensor',),
        ),
        migrations.CreateModel(
            name='SensorTemperatura',
            fields=[
                ('sensor_ptr', models.OneToOneField(primary_key=True, auto_created=True, serialize=False, parent_link=True, to='raspirover.Sensor')),
                ('temperatura', models.FloatField(null=True)),
            ],
            bases=('raspirover.sensor',),
        ),
        migrations.AddField(
            model_name='exploracion',
            name='sensor',
            field=models.ManyToManyField(to='raspirover.Sensor'),
        ),
        migrations.AddField(
            model_name='exploracion',
            name='username',
            field=models.ForeignKey(to='raspirover.UserProfile'),
        ),
    ]
