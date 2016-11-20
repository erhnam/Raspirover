# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User 
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator

class Sensor(models.Model):
	id_sensor = models.AutoField(primary_key=True)
	nombre = models.CharField(max_length=50)
	descripcion = models.CharField(max_length=140)
	fecha = models.DateTimeField(auto_now_add=True, null=True)
	enable = models.BooleanField(default=False)


class sensorTemperatura(Sensor):
	temperatura = models.FloatField(null=True,
		validators=[
			MinValueValidator(-10),
			MaxValueValidator(50)
		])	

	def __unicode__(self):
		return u'%s' % (self.nombre)


class sensorHumedad(Sensor):
	humedad = models.FloatField(null=True,
		validators=[
			MinValueValidator(-10),
			MaxValueValidator(50)
		])	
	
	def __unicode__(self):
		return u'%s' % (self.nombre)
	
class sensorLuz(Sensor):
	luz = models.IntegerField(null=True)
	
	def __unicode__(self):
		return u'%s' % (self.nombre)

class sensorGas(Sensor):
	gas = models.IntegerField(null=True)
	
	def __unicode__(self):
		return u'%s' % (self.nombre)


class Exploracion(models.Model):
	id_exploracion = models.AutoField(primary_key=True)
	sensorTemperatura = models.ManyToManyFields(sensorTemperatura, null=True, blank=True)
	sensorHunedad = models.ManyToManyFields(sensorHumedad, null=True, blank=True)
	sensorLuz = models.ManyToManyFields(sensorLuz, null=True, blank=True)
	sensorGas = models.ManyToManyFields(sensorGas, null=True, blank=True)
	usuario = models.ForeignKey(UserProfile, null=False)
	nombre = models.CharField(max_length=50, blank=False)
	fecha = models.DateTimeField(auto_now_add=True, null=True)
	descripcion = models.CharField(max_length=140, null=True)
	tiempo = models.DecimalField(max_digits=3, decimal_places=1, validators=[MaxValueValidator(10)], null=True)

	def __unicode__(self):
		return u'%s' % (self.nombre)	
		
class Sensores(models.Model):
	nombre = models.CharField(max_length=12, blank=False)
	temperatura = models.BooleanField()
	humedad = models.BooleanField()
	gas = models.BooleanField()
	luz = models.BooleanField()
	camara = models.BooleanField()
	descripcion = models.CharField(max_length=140, null=True)
	tiempo = models.DecimalField(max_digits=3, decimal_places=1, validators=[MaxValueValidator(10)], null=True)

