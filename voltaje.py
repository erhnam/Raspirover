import spidev
import globales

class CalcularVoltaje(object):
	#Constructor recibe el pin trigger y echo del sensor
	def __init__(self, canal, resistencia1, resistencia2):
		# SPI bus
		self.spi = spidev.SpiDev()
		self.spi.open(0,0)
		self.R1 = resistencia1
		self.R2 = resistencia2
		self.canal = canal

	# Funcion que lee el dato del SPI desde el chip MCP3008
	def leerCanal(self):
		adc = self.spi.xfer2([1,(8+self.canal)<<4,0])
		dato = ((adc[1]&3) << 8) + adc[2]
		return dato

	# Funcion que convierte el dato en voltaje
	# redondeado a dos decimales
	def convertirDatoAVoltios(self,dato,decimales):
		vout = (dato * 5) / float(1023)
		vin = vout / (self.R2/(self.R1+self.R2))
		vin = round(vin, decimales)
		if (vin < 0.09):
			vin = 0.0

		return vin

	# Funcion que ejecuta el valor del voltaje
	def calcularVoltaje(self):
		valorAnalogico = self.leerCanal()
		globales.voltaje = self.convertirDatoAVoltios(valorAnalogico,2)
		globales.porcentaje = int((globales.voltaje*100)/12.61)
