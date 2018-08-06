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
		#Lux
		self.MAX_ADC_READING = 1023  # 10bit adc 2^10 == 1023
		self.ADC_REF_VOLTAGE = 5.0 # 5 volts
		self.REF_RESISTANCE  = 10030 # 10k resistor 
		self.LUX_CALC_SCALAR = 12518931 # Formula 
		self.LUX_CALC_EXPONENT = -1.405  # exponent first calculated with calculator 

		#GAS
		self.calibration = False
		self.RL_VALUE = 5   #define the load resistance on the board, in kilo ohms
		self.RO_CLEAN_AIR_FACTOR = 9.83  #RO_CLEAR_AIR_FACTOR=(Sensor resistance in clean air)/RO,
									 #which is derived from the chart in datasheet
		#/**********************Application Related Macros**********************************/
		self.GAS_LPG = 0
		self.GAS_CO = 1
		self.GAS_SMOKE =2

		self.LPGCurve = [2.3,0.21,-0.47]
		self.COCurve = [2.3,0.72,-0.34]
		self.SmokeCurve = [2.3,0.53,-0.44]
		self.Ro = 10

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
		#calibration for first time
		if self.calibration == False:
				val = 0.0
				for x in range(50):
						raw_adc = self.LeerCanal(self.canalGas)
						val += float(self.RL_VALUE*(1023.0-raw_adc)/float(raw_adc))
				val = val / 50
				self.Ro = val/self.RO_CLEAN_AIR_FACTOR
#				print("Ro: %f kohm\n" % self.Ro)
				self.calibration = True

		raw_adc = self.LeerCanal(self.canalGas)
		read = raw_adc/self.Ro
		# Obtain % is ppm/10000
		globales.gas = (math.pow(10,( ((math.log(read)-self.LPGCurve[1])/ self.LPGCurve[2]) + self.LPGCurve[0])))/10000
		globales.co = (math.pow(10,( ((math.log(read)-self.COCurve[1])/ self.COCurve[2]) + self.COCurve[0])))/10000
		globales.smoke = (math.pow(10,( ((math.log(read)-self.SmokeCurve[1])/ self.SmokeCurve[2]) + self.SmokeCurve[0])))/10000

	#Funcion que devuelve el Fuego
	def ObtenerFuego(self):
		'''
		y = 0.7616x - 5.3018
		y = distance in inches, x = ADC counts
		'''
		#0 hay  mucho fuego 1023 ausencia de fuego.
		data = self.LeerCanal(self.canalFuego)
		#print("Fuego: %f" % data)
		#inches = 0.7616 * data - 5.3018;
		#globales.fuego = inches * 2.54 # 2.54 to get cm
		globales.fuego = (data*100)/1023 # cm -> 1023 es 100 cm

	#Funcion que devuelve la Luz
	def ObtenerLuz(self):
		''' 
		Intensidad de la luz diurna bajo diversas condiciones
		Iluminancia		Ejemplo
		120000 lux	Luz diurna más brillante
		110000 lux	Luz diurna brillante
		20000 lux	Sombra iluminada por un cielo completamente azul, al mediodía.
		10000 - 25000 lux	Típico día nublado o al mediodía.
		<200 lux	Extremo de las más oscuras nubes tempestuosas y al mediodía.
		400 lux	Orto u ocaso en un día claro (iluminación ambiental).
		40 lux	Completamente nublado, en el orto/ocaso.
		<1 lux	Extremo de las más oscuras nubes tempestuosas, en el orto/ocaso.

		Para comparar, los niveles de iluminación en la noche son:

		<1 lux	Claro de luna1​
		0.25 lux	Luna llena en una noche clara2​
		0.01 lux	Cuarto de luna
		0.001 lux	Cielo claro en una noche sin luna
		0.0001 lux	Cielo nocturno nublado y sin luna
		0.00005 lux	Luz de estrellas
		'''

		data = self.LeerCanal(self.canalLuz)
		data = 1023 - data
		# RESISTOR VOLTAGE_CONVERSION
		# Convert the raw digital data back to the voltage that was measured on the analog pin
		resistorVoltage = float(data / self.MAX_ADC_READING * self.ADC_REF_VOLTAGE);
		# voltage across the LDR is the 5V supply minus the 5k resistor voltage
		ldrVoltage = self.ADC_REF_VOLTAGE - resistorVoltage;
  
		# LDR_RESISTANCE_CONVERSION
		# resistance that the LDR would have for that voltage  
		ldrResistance = ldrVoltage/resistorVoltage * self.REF_RESISTANCE;
  
		# LDR_LUX
		# Change the code below to the proper conversion from ldrResistance to ldrLux
		ldrLux = self.LUX_CALC_SCALAR * pow(ldrResistance, self.LUX_CALC_EXPONENT); #LUX

		if ldrLux > 400:
			#Se detecta luz y apaga leds
			GPIO.output(self.pinLed1,GPIO.LOW)
			GPIO.output(self.pinLed2,GPIO.LOW)
			globales.luz = ldrLux
		else:
			#No se detecta luz y enciende leds
			GPIO.output(self.pinLed1,GPIO.HIGH)
			GPIO.output(self.pinLed2,GPIO.HIGH)
			globales.luz = ldrLux

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
