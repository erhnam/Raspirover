import spidev
import globales

class CalcularVoltaje(object):
	#Vin Max = 12,60v
	#Constructor recibe el pin trigger y echo del sensor
	def __init__(self, canal, r1, r2):
		# SPI bus
		self.spi = spidev.SpiDev()
		self.spi.open(0,0)
		self.spi.max_speed_hz = 1000000
		self.R1 = r1
		self.R2 = r2
		self.canal = canal

	# Funcion que lee el dato del SPI desde el chip MCP3008
	def leerCanal(self):
		adc = self.spi.xfer2([1,(8+self.canal)<<4,0])
		dato = ((adc[1]&3) << 8) + adc[2]
		return dato

	# Funcion que convierte el dato en voltaje
	# redondeado a dos decimales
	def convertirDatoAVoltios(self,dato,decimales):
		vout = (dato * 5.03) / 1024.0
		vin = vout / (self.R2/(self.R1+self.R2))
		vin = round(vin, decimales)

		return vin

	# Funcion que ejecuta el valor del voltaje
	def calcularVoltaje(self, arg=[]):
		valorAnalogico = self.leerCanal()
		for x in range(0,24):
			globales.voltaje += self.convertirDatoAVoltios(valorAnalogico,2)

		globales.voltaje = round(globales.voltaje/25,2)
		valor = globales.voltaje - 10.50
		globales.porcentaje = round(((valor * 100)/2.1),2)
		globales.voltaje=0.0
		res = 0.0
