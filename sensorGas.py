import RPi.GPIO as GPIO
import globales

class SensorGas(object):
	def __init__(self,pinGas):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(pinGas, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
		self.pinGas = pinGas
	
	def comprobarGas(self):
		if GPIO.input(self.pinGas) == 0:
			print ("!!! Peligro: Se han Detectado Gases !!!")
			globales.gas=False

		else:
			print ("Fuera de Peligro")
			globales.gas=True

	def __del__(self):
		print ("Sensor de Gas destruido")
