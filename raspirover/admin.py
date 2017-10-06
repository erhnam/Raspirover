from django.contrib import admin
#from .models import UserProfile

from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from raspirover.models import Usuario
# Register your models here.

from .models import *

admin.site.register(Sensores)

class exploracionAdmin(admin.ModelAdmin):
    list_display = ( 'id_exploracion', 'nombre', 'usuariofk', 'fecha', 'descripcion', 'tiempo')
    list_display_links = ('id_exploracion', 'nombre')

admin.site.register(Exploracion, exploracionAdmin)

class SensorAdmin(admin.ModelAdmin):
    list_display = ( 'id_sensor', 'tipo', 'fecha', 'enable' )

admin.site.register(Sensor, SensorAdmin)

class LecturasAdmin(admin.ModelAdmin):
    list_display = ( 'dato','fecha' )

admin.site.register(Lecturas, LecturasAdmin)


admin.site.register(Usuario)
