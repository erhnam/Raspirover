from django.contrib import admin
from .models import UserProfile

# Register your models here.

from .models import *

admin.site.register(UserProfile)
admin.site.register(Sensores)

class exploracionAdmin(admin.ModelAdmin):
    list_display = ( 'id', 'nombre', 'usuario', 'fecha', 'descripcion', 'tiempo')
    list_display_links = ('id', 'nombre')

admin.site.register(Exploracion, exploracionAdmin)

class SensorAdmin(admin.ModelAdmin):
    list_display = ( 'id', 'tipo', 'fecha', 'enable' )

admin.site.register(Sensor, SensorAdmin)


class sensorTemperaturaAdmin(admin.ModelAdmin):
    list_display = ( 'id', 'tipo', 'fecha', 'enable', 'temperatura' )

admin.site.register(sensorTemperatura, sensorTemperaturaAdmin)


class sensorHumedadAdmin(admin.ModelAdmin):
    list_display = ( 'id', 'tipo', 'fecha', 'enable', 'humedad' )

admin.site.register(sensorHumedad, sensorHumedadAdmin)

class sensorLuzAdmin(admin.ModelAdmin):
    list_display = ( 'id', 'tipo', 'fecha', 'enable', 'luz' )

admin.site.register(sensorLuz, sensorLuzAdmin)

class sensorGasAdmin(admin.ModelAdmin):
    list_display = ( 'id', 'tipo', 'fecha', 'enable', 'gas' )

admin.site.register(sensorGas, sensorGasAdmin)

