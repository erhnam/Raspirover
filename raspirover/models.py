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
		unique_together = (("usuariofk", "id_exploracion"),)	

#medida del sensor Spi
class sensorDatoSpi(models.Model):
	data = models.PositiveSmallIntegerField(null=True)
	fecha = models.DateTimeField(auto_now_add=True, null=True)

#medida del sensor Gpio
class sensorDatoGpio(models.Model):
	data = models.DecimalField(max_digits=3, decimal_places=1, null=True, validators=[MinValueValidator(-10), MaxValueValidator(100)])
	fecha = models.DateTimeField(auto_now_add=True, null=True)

#medida del sensor Uart(Gps)
class sensorDatoUart(models.Model):
	lat = models.FloatField(default=0,  null=True)
	lon = models.FloatField(default=0,  null=True)
	fecha = models.DateTimeField(auto_now_add=True, null=True)
	
#Sensor de Gps
class sensorGps(Sensor):
	gps = models.ManyToManyField(sensorDatoUart)

	class Meta:
		db_table = 'SensorGps'	

	def __unicode__(self):
		return self.lat+","+self.lon

#Sensor de temperatura	
class sensorTemperatura(Sensor):
	temperatura = models.ManyToManyField(sensorDatoGpio)
	
	class Meta:
		db_table = 'SensorTemperatura'	

	def __unicode__(self):
		return self.tipo


#Sensor de humedad	
class sensorHumedad(Sensor):
	humedad = models.ManyToManyField(sensorDatoGpio)

	class Meta:
		db_table = 'SensorHumedad'

	def __unicode__(self):
		return self.tipo

#Medidas de luz
class sensorLuz(Sensor):
	luz = models.ManyToManyField(sensorDatoSpi)
	
	class Meta:
		db_table = 'SensorLuz'

	def __unicode__(self):
		return self.tipo

#medida de gas
class sensorGas(Sensor):
	gas = models.ManyToManyField(sensorDatoSpi)
	class Meta:
		db_table = 'SensorGas'

	def __unicode__(self):
		return self.tipo

#medida de fuego
class sensorFuego(Sensor):
	fuego = models.ManyToManyField(sensorDatoSpi)
	
	class Meta:
		db_table = 'SensorFuego'

	def __unicode__(self):
		return self.tipo
	
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

