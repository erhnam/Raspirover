from __future__ import unicode_literals
from django.db import models
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User 
from django.core.validators import MaxValueValidator

# Create your models here.

class UserProfile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True, related_name='user_profile')
	photo = models.ImageField(upload_to='profiles', blank=True, null=True)
	
	def __unicode__(self):
		return self.user.username

class Sensor(models.Model):
	id_sensor = models.AutoField(primary_key=True)
	nombre = models.CharField(max_length=50)
	descripcion = models.CharField(max_length=140)
	fecha = models.DateTimeField(auto_now_add=True, null=True)


class SensorTemperatura(Sensor):
	temperatura = models.FloatField(null=True)

	def __unicode__(self):
		return "Temperatura"
		
class SensorHumedad(Sensor):
	humedad = models.FloatField(null=True)

	def __unicode__(self):
		return "Humedad"
		
class SensorLuz(Sensor):
	luz = models.IntegerField(null=True)

	def __unicode__(self):
		return "Luz"
		
class SensorGas(Sensor):
	gas = models.IntegerField(null=True)

	def __unicode__(self):
		return "Gas"

class Exploracion(models.Model):
	id_exploracion = models.AutoField(primary_key=True)
	sensor = models.ManyToManyField(Sensor)
	username = models.ForeignKey(UserProfile)	
	nombre = models.CharField(max_length=50, blank=False)
	fecha = models.DateTimeField(auto_now_add=True, null=True)
	descripcion = models.CharField(max_length=140)
	tiempo = models.DecimalField(max_digits=3, decimal_places=1, validators=[MaxValueValidator(10)], null=True)

	def __unicode__(self):
		return self.nombre		


		
class Sensores(models.Model):
	nombre = models.CharField(max_length=12, blank=False)
	temperatura = models.BooleanField()
	humedad = models.BooleanField()
	gas = models.BooleanField()
	luz = models.BooleanField()
	camara = models.BooleanField()
	tiempo = models.DecimalField(max_digits=3, decimal_places=1, validators=[MaxValueValidator(10)], null=True)
