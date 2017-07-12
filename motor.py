import RPi.GPIO as GPIO


#Clase motor
class Motor(object):
	#gpioPinIn1 IN1
	#gpioPinIn2 IN2
	#velocidad pedida por usuario
	def __init__(self, gpioPinIn1, gpioPinIn2):
		GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(gpioPinIn1, GPIO.OUT)
		GPIO.setup(gpioPinIn2, GPIO.OUT)
		self.motorGpioPinA = gpioPinIn1
		self.motorGpioPinB = gpioPinIn2

	#Motor hacia adelante
	def Adelante(self):
		GPIO.output(self.motorGpioPinA, GPIO.LOW)
		GPIO.output(self.motorGpioPinB, GPIO.HIGH)

	#Motor hacia atrás
	def Atras(self):
		GPIO.output(self.motorGpioPinA, GPIO.HIGH)
		GPIO.output(self.motorGpioPinB, GPIO.LOW)

	#Motor parado
	def Parar(self):
		GPIO.output(self.motorGpioPinA, GPIO.LOW)
		GPIO.output(self.motorGpioPinB, GPIO.LOW)
