# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User 
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractUser, UserManager

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
	tipo = models.CharField(max_length=20, null=True)
	descripcion = models.CharField(max_length=140)
	fecha = models.DateTimeField(auto_now_add=True, null=True)
	enable = models.BooleanField(default=False)

	def __unicode__(self):
		return u'%s' % (self.tipo)	

	class Meta:
		db_table = 'Sensor'

#Exploración
class Exploracion(models.Model):
	id_exploracion = models.AutoField(db_column='ID_Exploracion', primary_key=True)
	sensores = models.ManyToManyField(Sensor)
	usuariofk = models.ForeignKey(Usuario, db_column='UsuarioFK')
	nombre = models.CharField(max_length=150, blank=False)
	fecha = models.DateTimeField(auto_now_add=True, null=True)
	descripcion = models.CharField(max_length=140, null=True)
	tiempo = models.DecimalField(max_digits=3, decimal_places=1, validators=[MaxValueValidator(10)], null=True)

	def __unicode__(self):
		return u'%s' % (self.nombre)	

	class Meta:
		db_table = 'Exploracion'	
		#La solucion es añadir este constraint para que no haya dos parejas iguales
		unique_together = (("usuariofk", "id_exploracion"),)	
	
#Medida de temperatura	
class temperatura(models.Model):
	fecha = models.DateTimeField(auto_now_add=True, null=True)
	temperatura = models.DecimalField(max_digits=3, decimal_places=1, null=True,
		validators=[
			MinValueValidator(-10),
			MaxValueValidator(50)
		])	

	class Meta:
		db_table = 'Temperatura'
		
#Sensor de Temperatura		
class sensorTemperatura(Sensor):
	temperaturafk = models.ForeignKey(temperatura, db_column='TemperaturaFK')

	class Meta:
		db_table = 'SensorTemperatura'
	
#Medida de humedad	
class humedad(models.Model):
	fecha = models.DateTimeField(auto_now_add=True, null=True)
	humedad = models.DecimalField(max_digits=3, decimal_places=1, null=True,
		validators=[
			MinValueValidator(-10),
			MaxValueValidator(50)
		])

	class Meta:
		db_table = 'Humedad'	

#Sensor de Humedad
class sensorHumedad(Sensor):
	humedadfk = models.ForeignKey(humedad, db_column='HumedadFK')

	class Meta:
		db_table = 'SensorHumedad'

#Medidas de luz
class luminosidad(models.Model):
	fecha = models.DateTimeField(auto_now_add=True, null=True)
	luminosidad = models.BooleanField(default=False)
	
	class Meta:
		db_table = 'Luminosidad'

#Sensor de Luz
class sensorLuz(Sensor):
	luminosidad = models.ForeignKey(luminosidad, db_column='LuminosidadFK')

	class Meta:
		db_table = 'SensorLuz'

#medida de gas
class gas(models.Model):
	fecha = models.DateTimeField(auto_now_add=True, null=True)
	gas = models.BooleanField(default=False)
	
	class Meta:
		db_table = 'Gas'
#Sensor de Gas
class sensorGas(Sensor):
	gas = models.ForeignKey(gas, db_column='GasFK')

	class Meta:
		db_table = 'SensorGas'

	
class Sensores(models.Model):
	nombre = models.CharField(max_length=12, blank=False)
	temperatura = models.BooleanField()
	humedad = models.BooleanField()
	gas = models.BooleanField()
	luz = models.BooleanField()
	camara = models.BooleanField()
	descripcion = models.CharField(max_length=140, null=True)
	tiempo = models.FloatField(default=0,  null=True)

