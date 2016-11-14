import RPi.GPIO as GPIO
from sensorDistancia import *
from sensorLuz import *
from sensorTemperatura import *
from sensorGas import *

#Variables globales
driver=0
sensordth=0
sensorgas=0
sensorluz=0
sensordistancia=0
distancia=0.0
temperatura=0.0
humedad= 0
gas= ' '
luz= ' '
camara= ' '
trigger= ' '
nombre= ' '
timerluz=' '
timergas=' '
timerdth=' '
auto=False
automatic=' '
sdistancia=False
stemperatura=False
shumedad=False
sgas=False
sluz=False
camara=False
tiempo=False
nombre=False

def inicializar():
	sensordth=0
	sensorgas=0
	sensorluz=0
	sensordistancia=0
	distancia=0.0
	temperatura=0.0
	humedad= 0
	gas= ' '
	luz= ' '
	camara= ' '
	trigger= ' '
	nombre= ' '
	timerluz=' '
	timergas=' '
	timerdth=' '
	automatic=' '
	auto=False
	sdistancia=False
	stemperatura=False
	shumedad=False
	sgas=False
	sluz=False
	camara=False
	tiempo=False
	nombre=False
	
	GPIO.cleanup()
	print ("Todo inizializado")
	
