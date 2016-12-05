from django.contrib import admin
#from .models import UserProfile

from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from raspirover.models import Usuario
# Register your models here.

from .models import *

#admin.site.register(UserProfile)
admin.site.register(Sensores)
admin.site.register(humedad)
admin.site.register(luminosidad)
admin.site.register(gas)

class temperaturaAdmin(admin.ModelAdmin):
    list_display = ( 'id' ,'temperatura', 'fecha')
	

admin.site.register(temperatura, temperaturaAdmin)

class exploracionAdmin(admin.ModelAdmin):
    list_display = ( 'id_exploracion', 'nombre', 'usuariofk', 'fecha', 'descripcion', 'tiempo')
    list_display_links = ('id_exploracion', 'nombre')

admin.site.register(Exploracion, exploracionAdmin)

class SensorAdmin(admin.ModelAdmin):
    list_display = ( 'id_sensor', 'tipo', 'fecha', 'enable' )

admin.site.register(Sensor, SensorAdmin)


class sensorTemperaturaAdmin(admin.ModelAdmin):
    list_display = ( 'id_sensor', 'tipo', 'fecha', 'enable' )

admin.site.register(sensorTemperatura, sensorTemperaturaAdmin)


class sensorHumedadAdmin(admin.ModelAdmin):
    list_display = ( 'id_sensor', 'tipo', 'fecha', 'enable')

admin.site.register(sensorHumedad, sensorHumedadAdmin)

class sensorLuzAdmin(admin.ModelAdmin):
    list_display = ( 'id_sensor', 'tipo', 'fecha', 'enable')

admin.site.register(sensorLuz, sensorLuzAdmin)

class sensorGasAdmin(admin.ModelAdmin):
    list_display = ( 'id_sensor', 'tipo', 'fecha', 'enable')

admin.site.register(sensorGas, sensorGasAdmin)


admin.site.register(Usuario)

