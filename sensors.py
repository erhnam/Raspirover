import RPi.GPIO as GPIO
import spidev
import time
import os
import globales

GPIO.setwarnings(False)

#Sensor ultrasónico HC-SR04
class SensorDistancia(object):
	#Constructor recibe el pin trigger y echo del sensor
	def __init__(self, pinTrigger, pinEcho, arg=[]):
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
		distancia = (transcurrido * 34300.0)/2.0
		return distancia

        #Funcion para conseguir mas precision en la medida de distancia
	def precisionDistancia(self):
                #Se calcula tres veces
		distancia1 = self.calcularDistancia()
		time.sleep(0.01)
		distancia2 = self.calcularDistancia()
		time.sleep(0.01)
		distancia3 = self.calcularDistancia()
		time.sleep(0.01)
                #Se suman las tres distancias
		distancia = distancia1 + distancia2 + distancia3
                #se divide entre tres pruebas
		distancia = distancia / 3.0
                #se almacena valor
		globales.distancia = distancia
		return distancia

#Sensores SPI
class SPI(object):
	def __init__(self, canalTemp=None, canalHum=None, canalGas=None, canalLuz=None):
		# Abrir puerto SPI
		self.spi = spidev.SpiDev()
		self.spi.open(0,0)
		self.canalTemp = canalTemp
		self.canalHum = canalHum
		self.canalGas = canalGas
		self.canalLuz = canalLuz
		self.pinLed1 = None
		self.pinLed2 = None

		if self.canalLuz is not None:
			self.pinLed1 = 20
			self.pinLed2 = 16
			GPIO.setmode(GPIO.BCM)
			GPIO.setup(self.pinLed1,GPIO.OUT)
			GPIO.setup(self.pinLed2,GPIO.OUT)
			
	#Funcion para leer el canal del ADC MCP3008
	def LeerCanal(self, canal):
		adc = self.spi.xfer2([1,(8+canal)<<4,0])
		data = ((adc[1]&3) << 8) + adc[2]
		return data
 
	#Funcion que devuelve el voltaje del canal del ADC MCP3008
	def ConvertirVoltios(self, data):
		volts = (data * 3.3) / float(1023)
		volts = round(volts,2)
		return volts
 
	#Funcion que devuelve la temperatura
	def ObtenerTemperatura(self):
		data = self.LeerCanal(self.canalTemp)
		temp = ((data * 500)/float(1023))-50
		temp = round(temp,2)
		globales.temperatura = temp

	#Funcion que devuelve la humedad
	def ObtenerHumedad(self):
		data = self.LeerCanal(self.canalHum)
		globales.humedad = hum

	#Funcion que devuelve el Gas
	def ObtenerGas(self):
		data = self.LeerCanal(self.canalGas)
		if data > 120:
			#Se detecta gas
			globales.gas = 1
		else:
			#No se detecta gas
			globales.gas = 0

	#Funcion que devuelve la Luz
	def ObtenerLuz(self):
		data = self.LeerCanal(self.canalLuz)
		print(data)
		if data < 400:
			#Se detecta luz y apaga leds
			GPIO.output(self.pinLed1,GPIO.LOW)
			GPIO.output(self.pinLed2,GPIO.LOW)
			globales.luz = 1
		else:
			#No se detecta luz y enciende leds
			GPIO.output(self.pinLed1,GPIO.HIGH)
			GPIO.output(self.pinLed2,GPIO.HIGH)
			globales.luz = 0

	def destroy(self):
		GPIO.cleanup()
