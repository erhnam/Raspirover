import RPi.GPIO as GPIO
from sensores import *

#Variables globales
salir=0
driver=0
dbtemperatura=''
dbhumedad=''
dbgas=''
dbluz=''
dbtiempo=0
sensordth=0
sensorgas=0
sensorluz=0
sensordistancia=0
distancia=0.0
temperatura=0.0
humedad= 0
gas= False
luz= False
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
	dbtemperatura=''
	dbhumedad=''
	dbgas=''
	dbluz=''
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
	
#	print ("Todo inizializado")
	
