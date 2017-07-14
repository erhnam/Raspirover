import RPi.GPIO as GPIO
import spidev
import time
import os
import globales

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

import Adafruit_DHT

#resetea los pins
def setup(*pins):
	GPIO.cleanup()
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	for pin in pins:
		GPIO.setup(pin, GPIO.OUT)
		GPIO.output(pin, GPIO.LOW)

#Funcion para la temperatura y la humedad 
#proporcionada por Adafruit
def comprobarth(arg=[]):
	#Sensor Adafruit
	sensor = Adafruit_DHT.AM2302
	#Obtiene los valores del sensor de temepratura y la humedad
	globales.humedad, globales.temperatura = Adafruit_DHT.read_retry(sensor, 12)
	#Redondea a 1 dígito decimal
	globales.temperatura = int((globales.temperatura * 100) + 0.5) / 100.0
	globales.humedad = int((globales.humedad * 100) + 0.5) / 100.0

#Sensores SPI
class SPI(object):
	def __init__(self, canalTemp=None, canalHum=None, canalGas=None, canalLuz=None, canalBateria=None):
		# Abrir puerto SPI
		self.spi = spidev.SpiDev()
		self.spi.open(0,0)
		self.spi.max_speed_hz = 1000000
		self.canalTemp = canalTemp
		self.canalHum = canalHum
		self.canalGas = canalGas
		self.canalLuz = canalLuz
		self.canalBateria = canalBateria
		self.pinLed1 = None
		self.pinLed2 = None
		self.R1 = None
		self.R2 = None

		#Se añade las resistncias usadas en el divisor de voltaje
		if self.canalBateria is not None:
			self.R1 = 18100
			self.R2 = 12000

		#Se añade los leds
		if self.canalLuz is not None:
			self.pinLed1 = 20
			self.pinLed2 = 16
			GPIO.setup(self.pinLed1,GPIO.OUT)
			GPIO.setup(self.pinLed2,GPIO.OUT)
			
	#Funcion para leer el canal del ADC MCP3008
	def LeerCanal(self, canal):
		adc = self.spi.xfer2([1,(8+canal)<<4,0])
		data = ((adc[1]&3) << 8) + adc[2]
		return data
 
	#Funcion que devuelve el voltaje del canal del ADC MCP3008
	def ConvertirVoltios(self, data):
		volts = (data * 3.3) / float(1024)
		volts = round(volts,2)
		return volts

 	#Funcion para convertir valor analogico en voltaje para la bateria
	def convertirDatoAVoltios(self,dato):
                vout = (dato * 5.03) / float(1024)
                vin = vout / (self.R2/(self.R1+self.R2))
                vin = round(vin,2)

                return vin

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
		if data > 300:
			#Se detecta gas
			globales.gas = 1
		else:
			#No se detecta gas
			globales.gas = 0

	#Funcion que devuelve la Luz
	def ObtenerLuz(self):
		data = self.LeerCanal(self.canalLuz)

		if data < 850:
			#Se detecta luz y apaga leds
			GPIO.output(self.pinLed1,GPIO.LOW)
			GPIO.output(self.pinLed2,GPIO.LOW)
			globales.luz = 1
		else:
			#No se detecta luz y enciende leds
			GPIO.output(self.pinLed1,GPIO.HIGH)
			GPIO.output(self.pinLed2,GPIO.HIGH)
			globales.luz = 0


	#Funcion que devuelve el voltaje de bateria
	def ObtenerBateria(self):
		data = self.LeerCanal(self.canalBateria)
		globales.voltaje = self.convertirDatoAVoltios(data)
		valor = globales.voltaje - 10.50
		globales.porcentaje = round(((valor * 100.0)/2.1),2)

	#Fin de la clase
	def destroy(self):
		time.sleep(1)
		GPIO.cleanup()


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
		if distancia < 0:
			distancia = 32.0
		return distancia

