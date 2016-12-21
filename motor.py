import RPi.GPIO as GPIO

#Clase motor
class Motor(object):
	#gpioPinIn1 IN1
	#gpioPinIn2 IN2
	#enablePin para PWN
	#velocidad pedida por usuario
	def __init__(self, gpioPinIn1, gpioPinIn2, enablePin, velocidad):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(gpioPinIn1, GPIO.OUT)
		GPIO.setup(gpioPinIn2, GPIO.OUT)
		self.motorGpioPinA = gpioPinIn1
		self.motorGpioPinB = gpioPinIn2
		self.velocidad = velocidad
		self.pwm = enablePin
		GPIO.setup(self.pwm, GPIO.OUT)
		self.pwm  = GPIO.PWM(self.pwm,self.velocidad)
		self.pwm.start(0)
		self.pwm.ChangeDutyCycle(0)

	#Motor hacia adelante
	def Adelante(self):
		GPIO.output(self.motorGpioPinA, GPIO.LOW)
		GPIO.output(self.motorGpioPinB, GPIO.HIGH)
		self.pwm.ChangeDutyCycle(self.velocidad)

	#Motor hacia atrás
	def Atras(self):
		GPIO.output(self.motorGpioPinA, GPIO.HIGH)
		GPIO.output(self.motorGpioPinB, GPIO.LOW)
		self.pwm.ChangeDutyCycle(self.velocidad)

	#Motor parado
	def Parar(self):
		GPIO.output(self.motorGpioPinA, GPIO.LOW)
		GPIO.output(self.motorGpioPinB, GPIO.LOW)
		self.pwm.ChangeDutyCycle(0)
		
