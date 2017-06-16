from .models import *
from .forms import *
from servo import *
from motor import *
from camara import *
from dosMotores import *
from sensores import *
from globales import * 
from voltaje import *
from manager import *

class RR(object):
	self._motorIzq = Motor (27,22) 
	self._motorDer = Motor (5,6)
	self._driver = DriverDosMotores (self._motorIzq, self._motorDer)
	self._sensorluz = SensorLuz(21,20,16)
	self._sensorgas = SensorGas(26)
	self._servo = comprobarth()
	self._voltaje = CalcularVoltaje(1, 19500, 12000)
	