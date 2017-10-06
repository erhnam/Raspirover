# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User 
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractUser, UserManager
import django_extensions

# Create your models here.
#Usuario
class Usuario(AbstractUser):
	id_usuario = models.AutoField(db_column='ID_Usuario', primary_key=True)
	photo = models.ImageField(upload_to='profiles', blank=True, null=True)

	objects = UserManager()

	class Meta:
		db_table = 'Usuario'

#Sensor
class Sensor(models.Model):
	id_sensor = models.AutoField(db_column='ID_Sensor', primary_key=True)
	tipo = models.CharField(max_length=20)
	fecha = models.DateTimeField(auto_now_add=True, null=True)
	enable = models.BooleanField(default=False)

	def __unicode__(self):
		return u'%s' % (self.tipo)	

	class Meta:
		db_table = 'Sensor'

class Lecturas(models.Model):
	id_lecturas = models.AutoField(db_column='ID_Lecturas', primary_key=True)
	dato = models.CharField(max_length=22)
	fecha = models.DateTimeField(null=True)
	sensor = models.ForeignKey(Sensor, db_column='SensorFK', on_delete=models.CASCADE, null=True)

	def __unicode__(self):
		return u'%s' % (self.dato)	

	class Meta:
		db_table = 'Lecturas'


#Exploración
class Exploracion(models.Model):
	id_exploracion = models.AutoField(db_column='ID_Exploracion', primary_key=True)
	sensores = models.ManyToManyField(Sensor)
	usuariofk = models.ForeignKey(Usuario, db_column='UsuarioFK', on_delete=models.CASCADE)
	nombre = models.CharField(max_length=150, blank=False)
	fecha = models.DateTimeField(auto_now_add=True, null=True)
	descripcion = models.CharField(max_length=140, null=True)
	tiempo = models.DecimalField(max_digits=3, decimal_places=1, validators=[MaxValueValidator(10)], null=True)

	def __unicode__(self):
		return u'%s' % (self.nombre)	

	class Meta:
		db_table = 'Exploracion'	
		#La solucion es añadir este constraint para que no haya dos parejas iguales
		#unique_together = (("usuariofk", "id_exploracion"),)	

	
class Sensores(models.Model):
	nombre = models.CharField(max_length=12, null=True)
	temperatura = models.BooleanField()
	humedad = models.BooleanField()
	gas = models.BooleanField()
	fuego = models.BooleanField()	
	luz = models.BooleanField()
	camara = models.BooleanField()
	descripcion = models.CharField(max_length=140, null=True)
	tiempo = models.FloatField(default=0,  null=True)

