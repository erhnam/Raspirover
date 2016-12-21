import RPi.GPIO as GPIO
from sensores import *

#Variables globales
salir=0				#Controla la salida del modo auto o manual
driver=0			#Controlador del motor
dbtemperatura=''	#Base de datos de temperatura
dbhumedad=''		#Base de datos de humedad
dbgas=''			#Base de datos de gas
dbluz=''			#Base de datos de luz
dbtiempo=0			#Base de datos de tiempo
sensordth=0			#Sensor DTH22
sensorgas=0			#Sensor de gas
sensorluz=0			#Sensor de luz
distancia=0.0		#Distancia proporcionada por el sensor
temperatura=0.0		#Valor de la temperatura
humedad=0.0			#Valor de la humedad
gas= 0				#Valor de gas
luz= 0				#Valor de luz
trigger= ' '		#Trigger para almacenar los datos
timerluz=' '		#Timer para sensor de luz
timergas=' '		#Timer para sensor de gas
timerdth=' '		#Timer para sensor de DTH22
auto=False          #Variable para detectar modo automatico
automatic=' '		#Variable que carga hilo de modo automatico
sdistancia=False    #Variable del sensor distancia del formulario 
stemperatura=False  #Variable del sensor temperatura del formulario
shumedad=False      #Variable del sensor humedad del formulario
sgas=False          #Variable del sensor gas del formulario
sluz=False          #Variable del sensor luz del formulario
camara=False        #Variable de la camara del formulario
tiempo=False        #Variable de tiempo del formulario 
nombre=False        #Variable del nombre del formulario

#Funcion que inicializa las variables
def inicializar():
	dbtemperatura=''
	dbhumedad=''
	dbgas=''
	dbluz=''
	driver=0
	sensordth=0
	sensorgas=0
	sensorluz=0
	distancia=0.0
	temperatura=0.0
	humedad= 0
	gas= 0
	luz= 0
	camara= ' '
	trigger= ' '
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
