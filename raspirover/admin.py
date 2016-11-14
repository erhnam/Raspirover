from django.contrib import admin
from .models import UserProfile

# Register your models here.

from .models import *

admin.site.register(Sensor)
admin.site.register(SensorTemperatura)
admin.site.register(SensorHumedad)
admin.site.register(SensorLuz)
admin.site.register(SensorGas)
admin.site.register(Exploracion)
admin.site.register(UserProfile)
admin.site.register(Sensores)

