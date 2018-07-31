# -*- encoding: utf-8 -*-

import RPi.GPIO as GPIO
import spidev
import time
import os
import globales
import Adafruit_DHT
import serial
import math

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

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
	hum, temp = Adafruit_DHT.read_retry(sensor, 2)
	if hum != 0.0 and temp != 0.0:
		globales.humedad = hum
		globales.temperatura = temp
		#Redondea a 1 dígito decimal
		globales.temperatura = round(globales.temperatura,1)
		globales.humedad = round(globales.humedad,1)

#Clase del sensor GPS
class GPS():
	def __init__(self):
		self.gps = serial.Serial("/dev/ttyAMA0", baudrate = 9600)
		self.coord = None
		self.direccion = None

	#Funcion que convierte los minutos devueltos por protocolo NMEA a grados
	def minutos_a_grados(self, coord, direccion):
		coord_float = coord/100.0;
		coord_grados = math.floor(coord_float)+(coord_float%1.0)/0.6
		if direccion =="S" or direccion == "W":
			coord_grados = coord_grados * -1.0;

		if round(coord_grados,6) != 0.0:
			return round(coord_grados,6)


	#Función que lee los datos del protocolo NMEA
	def leer(self):
		for i in range(0,14):
			line = self.gps.readline()
			data = str(line).split(",")
#			print(data)
			if data[0] == "b'$GNRMC":
				if data[2] == "A":
					lat, latd = float(data[3]), data[4]
					lon, lond = float(data[5]), data[6]
					
					globales.lat = self.minutos_a_grados(lat, latd)
					globales.lon = self.minutos_a_grados(lon, lond)
						
					print("%s , %s\n" % (globales.lat, globales.lon))

#Sensores SPI
class SPI(object):
	def __init__(self, canalTemp=None, canalHum=None, canalGas=None, canalLuz=None, canalBateria=None, canalFuego=None):
		# Abrir puerto SPI
		"""
		125.0 MHz 	125000000
		62.5 MHz 	62500000
		31.2 MHz 	31200000
		15.6 MHz 	15600000
		7.8 MHz 	7800000
		3.9 MHz 	3900000
		1953 kHz 	1953000
		976 kHz 	976000
		488 kHz 	488000
		244 kHz 	244000
		122 kHz 	122000
		61 kHz 		61000
		30.5 kHz 	30500
		15.2 kHz 	15200
		7629 Hz 	7629
		"""
		self.spi = spidev.SpiDev()
		self.spi.open(0,0)
		self.spi.max_speed_hz=30500
		self.canalTemp = canalTemp
		self.canalHum = canalHum
		self.canalFuego = canalFuego
		self.canalGas = canalGas
		self.canalLuz = canalLuz
		self.canalBateria = canalBateria
		self.pinLed1 = None
		self.pinLed2 = None
		self.R1 = None
		self.R2 = None

		#Se añade las resistncias usadas en el divisor de voltaje
		if self.canalBateria is not None:
			self.R1 = 30000.0
			self.R2 = 7500.0

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
		volts = (data * 5.0) / 1024.0
		volts = round(volts,2)
		return volts

	#Funcion para convertir valor analogico en voltaje para la bateria
	def convertirDatoAVoltios(self,dato):
		vout = float((dato * 5.0) / 1024.0)
		vin = float(vout / (self.R2/(self.R1+self.R2)))
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
		globales.humedad = self.LeerCanal(self.canalHum)

	#Funcion que devuelve el Gas
	def ObtenerGas(self):
		globales.gas = self.LeerCanal(self.canalGas)

	#Funcion que devuelve el Gas
	def ObtenerFuego(self):
		data = self.LeerCanal(self.canalFuego)
		globales.fuego = 1023 - data
#		print("Fuego: %d\n" % (globales.fuego) )

	#Funcion que devuelve la Luz
	def ObtenerLuz(self):
		data = self.LeerCanal(self.canalLuz)
		data = 1023 - data
		if data > 350:
			#Se detecta luz y apaga leds
			GPIO.output(self.pinLed1,GPIO.LOW)
			GPIO.output(self.pinLed2,GPIO.LOW)
			globales.luz = data
		else:
			#No se detecta luz y enciende leds
			GPIO.output(self.pinLed1,GPIO.HIGH)
			GPIO.output(self.pinLed2,GPIO.HIGH)
			globales.luz = data

	#Funcion que devuelve el voltaje de bateria
	def ObtenerBateria(self):
		data = self.LeerCanal(self.canalBateria)
		globales.voltaje = self.convertirDatoAVoltios(data)
		valor = globales.voltaje - 10.50
		globales.porcentaje = round(((valor * 100.0)/2.1),2)
#		print("Bateria: %f\n" % (globales.porcentaje) )

	#Fin de la clase
	def destroy(self):
		time.sleep(1)
		GPIO.cleanup()

#Sensor ultrasónico HC-SR04
class SensorDistancia(object):
	timeout = 0.05

	def __init__(self, channel):
		self.channel = channel
		GPIO.setmode(GPIO.BCM)

	def calcularDistancia(self):
		pulse_end = 0
		pulse_start = 0
		GPIO.setup(self.channel,GPIO.OUT)
		GPIO.output(self.channel, False)
		time.sleep(0.01)
		GPIO.output(self.channel, True)
		time.sleep(0.00001)
		GPIO.output(self.channel, False)
		GPIO.setup(self.channel,GPIO.IN)

		timeout_start = time.time()
		while GPIO.input(self.channel)==0:
			pulse_start = time.time()
			if pulse_start - timeout_start > self.timeout:
				return 32.0
		while GPIO.input(self.channel)==1:
			pulse_end = time.time()
			if pulse_start - timeout_start > self.timeout:
				return 32.0

		if pulse_start != 0 and pulse_end != 0:
			pulse_duration = pulse_end - pulse_start
			distance = (pulse_duration * 100 * 343.0) /2
			distance = distance
			print (distance)
			if distance >= 0:
				return distance
			else:
				return 32.0
		else :
			return 32.0
