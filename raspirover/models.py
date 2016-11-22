# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User 
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

class UserProfile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL,primary_key=True)
	photo = models.ImageField(upload_to='profiles', blank=True, null=True)
	
	def __unicode__(self):
		return self.user.username

class Sensor(models.Model):
	tipo = models.CharField(max_length=20, null=True)
	descripcion = models.CharField(max_length=140)
	fecha = models.DateTimeField(auto_now_add=True, null=True)
	enable = models.BooleanField(default=False)

	def __unicode__(self):
		return u'%s' % (self.tipo)	

class Exploracion(models.Model):
	sensores = models.ManyToManyField(Sensor)
	usuario = models.ForeignKey(UserProfile, null=True)
	nombre = models.CharField(max_length=150, unique=True, blank=False)
	fecha = models.DateTimeField(auto_now_add=True, null=True)
	descripcion = models.CharField(max_length=140, null=True)
	tiempo = models.DecimalField(max_digits=3, decimal_places=1, validators=[MaxValueValidator(10)], null=True)

	def __unicode__(self):
		return u'%s' % (self.nombre)	
		
class sensorTemperatura(Sensor):
	temperatura = models.DecimalField(max_digits=3, decimal_places=1, null=True,
		validators=[
			MinValueValidator(-10),
			MaxValueValidator(50)
		])	

class sensorHumedad(Sensor):
	humedad = models.DecimalField(max_digits=3, decimal_places=1, null=True,
		validators=[
			MinValueValidator(-10),
			MaxValueValidator(50)
		])	
	
class sensorLuz(Sensor):
	luz = models.BooleanField(default=False)
	
class sensorGas(Sensor):
	gas = models.IntegerField(default=False)
	
class Sensores(models.Model):
	nombre = models.CharField(max_length=12, blank=False)
	temperatura = models.BooleanField()
	humedad = models.BooleanField()
	gas = models.BooleanField()
	luz = models.BooleanField()
	camara = models.BooleanField()
	descripcion = models.CharField(max_length=140, null=True)
	tiempo = models.FloatField(default=0,  null=True)

