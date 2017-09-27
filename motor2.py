import RPi.GPIO as GPIO

#Clase motor
class Motor(object):
	#gpioPinIn1 IN1
	#gpioPinIn2 IN2
	#velocidad pedida por usuario
	def __init__(self, gpioPinIn1, gpioPinIn2, gpioPinEn):
		
		GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BCM)
		self.pinA = gpioPinIn1
		self.pinB = gpioPinIn2
		self.pinControl = gpioPinEn
		self.speed = 30

		GPIO.setup(self.pinA, GPIO.OUT)
		GPIO.setup(self.pinB, GPIO.OUT)
		GPIO.setup(self.pinControl, GPIO.OUT)

		self.pwm_adelante = GPIO.PWM(self.pinA, 100)
		self.pwm_adelante.start(0)

		self.pwm_atras = GPIO.PWM(self.pinB, 100)
		self.pwm_atras.start(0)

		GPIO.output(self.pinControl,GPIO.HIGH)

	#Motor hacia adelante
	def Adelante(self):
		self.pwm_adelante.ChangeDutyCycle(0)
		self.pwm_atras.ChangeDutyCycle(self.speed)

	#Motor hacia atrás
	def Atras(self):
		self.pwm_adelante.ChangeDutyCycle(self.speed)
		self.pwm_atras.ChangeDutyCycle(0)

	#Motor parado
	def Parar(self):
		self.pwm_adelante.ChangeDutyCycle(0)
		self.pwm_atras.ChangeDutyCycle(0)

	#Cambiar la velodidad
	def SetSpeed(self, speed):
		self.speed = speed
		print ("Speed: %d" % (self.speed))
			

