import RPi.GPIO as GPIO
import time
import globales
import Adafruit_DHT

#resetea los pins
def setup(*pins):
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    for pin in pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)


#Funcion para la temperatura y la humedad 
#proporcionada por Adafruit
def comprobarth():
	#Sensor Adafruit
	sensor = Adafruit_DHT.AM2302
	#Obtiene los valores del sensor de temepratura y la humedad
	globales.humedad, globales.temperatura = Adafruit_DHT.read_retry(sensor, 14)
	#Redondea a 1 dígito decimal
	globales.temperatura = int((globales.temperatura * 100) + 0.5) / 100.0	
	globales.humedad = int((globales.humedad * 100) + 0.5) / 100.0	

#Sensor ultrasónico HC-SR04
class SensorDistancia(object):
	#Constructor recibe el pin trigger y echo del sensor
	def __init__(self, pinTrigger, pinEcho):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(pinTrigger,GPIO.OUT)
		GPIO.setup(pinEcho,GPIO.IN)
		GPIO.output(pinTrigger, False)
		self.echo = pinEcho
		self.trigger = pinTrigger

	#funcion que calcula la distancia		
	def calcularDistancia(self):
		#Se crean las variables para controlar tiempo
		inicio = 0
		fin = 0
		#Manda señal
		GPIO.output(self.trigger, True)
		#Espera respuesta
		time.sleep(0.00001)
		#Recoge la señal
		GPIO.output(self.trigger, False)

		#Manda señal de inicio
		while GPIO.input(self.echo)==0:
			inicio = time.time()
		#Recibe la señal
		while GPIO.input(self.echo)==1:
			fin = time.time()

		#Calculo del tiempo tardado
		transcurrido = fin-inicio
		#Formula para la distancia
		distancia = (transcurrido * 34300)/2
		#se almacena la distancia
		globales.distancia = distancia		
		return distancia

	#Funcion para conseguir mas precision en la medida de distancia
	def precisionDistancia(self):
		#Se calcula tres veces
		distancia1 = self.calcularDistancia()
		time.sleep(0.1)
		distancia2 = self.calcularDistancia()
		time.sleep(0.1)
		distancia3 = self.calcularDistancia()
		time.sleep(0.1)
		#Se suman las tres distancias
		distancia = distancia1 + distancia2 + distancia3
		#se divide entre tres pruebas
		distancia = distancia / 3
		#se almacena valor
		globales.distancia = distancia
		return distancia

	#Funcion que destruye el sensor
	def __del__(self):
		print ("Sensor de Distancia destruido")

#Sensor de Luz
class SensorLuz(object):
	#Constructor recibe el pin del sensor, y de los dos leds
	def __init__(self, pinSensor, pinLed1, pinLed2):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(pinSensor,GPIO.IN)
		GPIO.setup(pinLed1,GPIO.OUT)
		GPIO.setup(pinLed2,GPIO.OUT)
		self.sensor=pinSensor
		self.led1=pinLed1
		self.led2=pinLed2

	def comprobarLuz(self):
		#Detecta que hay Luz
		if (GPIO.input(self.sensor) == 0):
			GPIO.output(self.led1,GPIO.LOW)
			GPIO.output(self.led2,GPIO.LOW)
			globales.luz = 1
		#Detecta que no hay luz y enciende los leds
		else:
			GPIO.output(self.led1,GPIO.HIGH)
			GPIO.output(self.led2,GPIO.HIGH)
			globales.luz = 0

	#Funcion que destruye el sensor
	def __del__(self):
		print ("Sensor de Luz destruido")

#Sensor de gas MQ2
class SensorGas(object):
	#Constructor que recibe el pin del sensor
	def __init__(self,pinGas):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(pinGas, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
		self.pinGas = pinGas

	#Funcion que comprueba si detecta gases
	def comprobarGas(self):
		#Se detectan gases
		if GPIO.input(self.pinGas) == 0:
			globales.gas=1

		#No se detectan gases
		else:
			globales.gas=0

	#Funcion que destruye el sensor
	def __del__(self):
		print ("Sensor de Gas destruido")


