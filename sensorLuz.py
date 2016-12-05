import RPi.GPIO as GPIO
import time
import globales

class SensorLuz(object):
	def __init__(self, pinSensor, pinLed1, pinLed2):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(pinSensor,GPIO.IN)
		GPIO.setup(pinLed1,GPIO.OUT)
		GPIO.setup(pinLed2,GPIO.OUT)
		self.sensor=pinSensor
		self.led1=pinLed1
		self.led2=pinLed2

	def comprobarLuz(self):
		if (GPIO.input(self.sensor) == 0):
			GPIO.output(self.led1,GPIO.LOW)
			GPIO.output(self.led2,GPIO.LOW)
			globales.luz = False
		else:
			GPIO.output(self.led1,GPIO.HIGH)
			GPIO.output(self.led2,GPIO.HIGH)
			globales.luz = True

	def __del__(self):
		print ("Sensor de Luz destruido")
