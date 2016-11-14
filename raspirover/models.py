from __future__ import unicode_literals
from django.db import models
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User 
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

def validate_only_one_instance(object):
	"""
	Valida que solo exista una instancia del modelo
	"""
	model = object.__class__
	if (model.objects.count() > 0 and object.id != model.objects.get().id):
		raise ValidationError('Sólo una instancia del modelo %s es permitida.' % model.__name__)

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
	enable = models.BooleanField(default=False)

class SensorTemperatura(Sensor):
	temperatura = models.FloatField(null=True,
		validators=[
			MinValueValidator(-10),
			MaxValueValidator(50)
		])	

	def __unicode__(self):
		return u'%s' % (self.nombre)

	def clean(self):
		validate_only_one_instance(self)

	def save(self, *args, **kwargs):
		super(TemperatureSensor, self).save(*args, **kwargs)
		self.full_clean()
		if not self.name:
			self.name = 'SensorTemperatura' + str(self.id)
			self.save()


class SensorHumedad(Sensor):
	humedad = models.FloatField(null=True,
		validators=[
			MinValueValidator(-10),
			MaxValueValidator(50)
		])	
	
	def __unicode__(self):
		return u'%s' % (self.nombre)
	
	def clean(self):
		validate_only_one_instance(self)

	def save(self, *args, **kwargs):
		super(TemperatureSensor, self).save(*args, **kwargs)
		self.full_clean()
		if not self.name:
			self.name = 'SensorHumedad' + str(self.id)
			self.save()
				
class SensorLuz(Sensor):
	luz = models.IntegerField(null=True)
	
	def __unicode__(self):
		return u'%s' % (self.nombre)

	def clean(self):
		validate_only_one_instance(self)

	def save(self, *args, **kwargs):
		super(TemperatureSensor, self).save(*args, **kwargs)
		self.full_clean()
		if not self.name:
			self.name = 'SensorLuz' + str(self.id)
			self.save()

class SensorGas(Sensor):
	gas = models.IntegerField(null=True)
	
	def __unicode__(self):
		return u'%s' % (self.nombre)

	def clean(self):
		validate_only_one_instance(self)

	def save(self, *args, **kwargs):
		super(TemperatureSensor, self).save(*args, **kwargs)
		self.full_clean()
		if not self.name:
			self.name = 'SensorGas' + str(self.id)
			self.save()

class Exploracion(models.Model):
	id_exploracion = models.AutoField(primary_key=True)
	sensorTemperatura = models.ManyToManyField(SensorTemperatura, null=True, blank=True)
	sensorHunedad = models.ManyToManyField(SensorHumedad, null=True, blank=True)
	sensorLuz = models.ManyToManyField(SensorLuz, null=True, blank=True)
	sensorGas = models.ManyToManyField(SensorGas, null=True, blank=True)
	usuario = models.ForeignKey(UserProfile, null=False)
	nombre = models.CharField(max_length=50, blank=False)
	fecha = models.DateTimeField(auto_now_add=True, null=True)
	descripcion = models.CharField(max_length=140)
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
	descripcion = models.CharField(max_length=100)
	tiempo = models.DecimalField(max_digits=3, decimal_places=1, validators=[MaxValueValidator(10)], null=True)

