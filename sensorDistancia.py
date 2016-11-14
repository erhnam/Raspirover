import time
import RPi.GPIO as GPIO
import globales


class SensorDistancia(object):
	def __init__(self, pinTrigger, pinEcho):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(pinTrigger,GPIO.OUT)
		GPIO.setup(pinEcho,GPIO.IN)
		GPIO.output(pinTrigger, False)
		self.echo = pinEcho
		self.trigger = pinTrigger
			
	def calcularDistancia(self):
		GPIO.output(self.trigger, True)
		time.sleep(0.00001)
		GPIO.output(self.trigger, False)
		inicio = time.time()

		while GPIO.input(self.echo)==0:
			inicio = time.time()

		while GPIO.input(self.echo)==1:
			fin = time.time()

		transcurrido = fin-inicio
		distancia = (transcurrido * 34300)/2
		return distancia

	def precisionDistancia(self):
		distancia1 = self.calcularDistancia()
		time.sleep(0.1)
		distancia2 = self.calcularDistancia()
		time.sleep(0.1)
		distancia3 = self.calcularDistancia()
		distancia = distancia1 + distancia2 + distancia3
		distancia = distancia / 3
		globales.distancia = distancia
		return distancia
		
	def __del__(self):
		print ("Sensor de Distancia destruido")
