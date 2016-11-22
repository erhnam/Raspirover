import RPi.GPIO as GPIO
import time
import globales

class SensorLuz(object):
	def __init__(self, pinSensor, pinLed):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(pinSensor,GPIO.IN)
		GPIO.setup(pinLed,GPIO.OUT)
		self.sensor=pinSensor
		self.led=pinLed

	def comprobarLuz(self):
		if (GPIO.input(self.sensor) == 0):
			print ("Hay Luz")
			GPIO.output(self.led,GPIO.HIGH)
			globales.luz = False
		else:
			print ("No hay luz")
			GPIO.output(self.led,GPIO.LOW)
			globales.luz = True

	def __del__(self):
		print ("Sensor de Luz destruido")
