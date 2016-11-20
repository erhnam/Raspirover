from django.contrib import admin
from .models import UserProfile

# Register your models here.

from .models import *

admin.site.register(Sensor)
admin.site.register(sensorTemperatura)
admin.site.register(sensorHumedad)
admin.site.register(sensorLuz)
admin.site.register(sensorGas)
admin.site.register(Exploracion)
admin.site.register(UserProfile)
admin.site.register(Sensores)

