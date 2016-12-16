# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.auth.models
import django.core.validators
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(verbose_name='last login', null=True, blank=True)),
                ('is_superuser', models.BooleanField(verbose_name='superuser status', help_text='Designates that this user has all permissions without explicitly assigning them.', default=False)),
                ('username', models.CharField(verbose_name='username', help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], max_length=30, error_messages={'unique': 'A user with that username already exists.'}, unique=True)),
                ('first_name', models.CharField(verbose_name='first name', max_length=30, blank=True)),
                ('last_name', models.CharField(verbose_name='last name', max_length=30, blank=True)),
                ('email', models.EmailField(verbose_name='email address', max_length=254, blank=True)),
                ('is_staff', models.BooleanField(verbose_name='staff status', help_text='Designates whether the user can log into this admin site.', default=False)),
                ('is_active', models.BooleanField(verbose_name='active', help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', default=True)),
                ('date_joined', models.DateTimeField(verbose_name='date joined', default=django.utils.timezone.now)),
                ('id_usuario', models.AutoField(serialize=False, primary_key=True, db_column='ID_Usuario')),
                ('photo', models.ImageField(blank=True, null=True, upload_to='profiles')),
                ('groups', models.ManyToManyField(verbose_name='groups', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', to='auth.Group', blank=True, related_query_name='user', related_name='user_set')),
                ('user_permissions', models.ManyToManyField(verbose_name='user permissions', help_text='Specific permissions for this user.', to='auth.Permission', blank=True, related_query_name='user', related_name='user_set')),
            ],
            options={
                'db_table': 'Usuario',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Exploracion',
            fields=[
                ('id_exploracion', models.AutoField(serialize=False, primary_key=True, db_column='ID_Exploracion')),
                ('nombre', models.CharField(max_length=150)),
                ('fecha', models.DateTimeField(auto_now_add=True, null=True)),
                ('descripcion', models.CharField(max_length=140, null=True)),
                ('tiempo', models.DecimalField(max_digits=3, decimal_places=1, validators=[django.core.validators.MaxValueValidator(10)], null=True)),
            ],
            options={
                'db_table': 'Exploracion',
            },
        ),
        migrations.CreateModel(
            name='Sensor',
            fields=[
                ('id_sensor', models.AutoField(serialize=False, primary_key=True, db_column='ID_Sensor')),
                ('tipo', models.CharField(max_length=20)),
                ('fecha', models.DateTimeField(auto_now_add=True, null=True)),
                ('enable', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'Sensor',
            },
        ),
        migrations.CreateModel(
            name='Sensores',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=12)),
                ('temperatura', models.BooleanField()),
                ('humedad', models.BooleanField()),
                ('gas', models.BooleanField()),
                ('luz', models.BooleanField()),
                ('camara', models.BooleanField()),
                ('descripcion', models.CharField(max_length=140, null=True)),
                ('tiempo', models.FloatField(default=0, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='sensorGas',
            fields=[
                ('sensor_ptr', models.OneToOneField(auto_created=True, serialize=False, parent_link=True, primary_key=True, to='raspirover.Sensor')),
                ('gas', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'SensorGas',
            },
            bases=('raspirover.sensor',),
        ),
        migrations.CreateModel(
            name='sensorHumedad',
            fields=[
                ('sensor_ptr', models.OneToOneField(auto_created=True, serialize=False, parent_link=True, primary_key=True, to='raspirover.Sensor')),
                ('humedad', models.DecimalField(max_digits=3, decimal_places=1, validators=[django.core.validators.MinValueValidator(-10), django.core.validators.MaxValueValidator(100)], null=True)),
            ],
            options={
                'db_table': 'SensorHumedad',
            },
            bases=('raspirover.sensor',),
        ),
        migrations.CreateModel(
            name='sensorLuz',
            fields=[
                ('sensor_ptr', models.OneToOneField(auto_created=True, serialize=False, parent_link=True, primary_key=True, to='raspirover.Sensor')),
                ('luz', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'SensorLuz',
            },
            bases=('raspirover.sensor',),
        ),
        migrations.CreateModel(
            name='sensorTemperatura',
            fields=[
                ('sensor_ptr', models.OneToOneField(auto_created=True, serialize=False, parent_link=True, primary_key=True, to='raspirover.Sensor')),
                ('temperatura', models.DecimalField(max_digits=3, decimal_places=1, validators=[django.core.validators.MinValueValidator(-10), django.core.validators.MaxValueValidator(100)], null=True)),
            ],
            options={
                'db_table': 'SensorTemperatura',
            },
            bases=('raspirover.sensor',),
        ),
        migrations.AddField(
            model_name='exploracion',
            name='sensores',
            field=models.ManyToManyField(to='raspirover.Sensor'),
        ),
        migrations.AddField(
            model_name='exploracion',
            name='usuariofk',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, db_column='UsuarioFK'),
        ),
        migrations.AlterUniqueTogether(
            name='exploracion',
            unique_together=set([('usuariofk', 'id_exploracion')]),
        ),
    ]
