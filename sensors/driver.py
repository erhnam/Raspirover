import RPi.GPIO as GPIO
import math
import Adafruit_PCA9685
import time

#       FRONT
#  M1S1       M6S6
#    \         /
#     \       /
#  M2-----------M5
#     /       \
#    /         \
#  M3S3       M4S4
#        REAR


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# 12 y 25 libres

class Servo(object):

	#Constructor
	def __init__(self, channel, servo_min = 150, servo_max = 600, frequency = 60):
		self.channel = channel
		self.servo_min = servo_min
		self.servo_max = servo_max
		self.frequency = frequency

	def setup(self):
		self.pwm = Adafruit_PCA9685.PCA9685()
		self.pwm.set_pwm_freq(self.frequency)

	def angle_to_pulse(self, val):
		oldRange = 180
		newRange = self.servo_max - self.servo_min
		return math.floor(((val * newRange) / oldRange) + self.servo_min)

	def setAngle(self, angle):
		if(angle < 0):
			angle = 0
		elif(angle > 180):
			angle = 180
		self.pwm.set_pwm(self.channel, 0, self.angle_to_pulse(angle))

class Driver(object):
	def __init__(self,M1,M2,M3,M4,M5,M6,S1,S3,S4,S6):
		self.M1 = M1
		self.M2 = M2
		self.M3 = M3
		self.M4 = M4
		self.M5 = M5
		self.M6 = M6
		self.S1 = S1
		self.S3 = S3
		self.S4 = S4
		self.S6 = S6
		self.S1.setAngle(90)
		self.S3.setAngle(90)
		self.S4.setAngle(90)
		self.S6.setAngle(90)

	def Adelante(self):
		self.S1.setAngle(90)
		self.S3.setAngle(90)
		self.S4.setAngle(90)
		self.S6.setAngle(90)
		self.M1.Adelante()
		self.M2.Adelante()
		self.M3.Adelante()
		self.M4.Adelante()
		self.M5.Adelante()
		self.M6.Adelante()

	def Atras(self):
		self.S1.setAngle(90)
		self.S3.setAngle(90)
		self.S4.setAngle(90)
		self.S6.setAngle(90)
		self.M1.Atras()
		self.M2.Atras()
		self.M3.Atras()
		self.M4.Atras()
		self.M5.Atras()
		self.M6.Atras()

	def Derecha(self):
		self.S1.setAngle(145)
		self.S3.setAngle(40)
		self.S4.setAngle(145)
		self.S6.setAngle(50)
		self.M1.Adelante()
		self.M2.Adelante()
		self.M3.Adelante()
		self.M4.Atras()
		self.M5.Atras()
		self.M6.Atras()

	def Izquierda(self):
		self.S1.setAngle(145)
		self.S3.setAngle(40)
		self.S4.setAngle(145)
		self.S6.setAngle(40)
		self.M1.Atras()
		self.M2.Atras()
		self.M3.Atras()
		self.M4.Adelante()
		self.M5.Adelante()
		self.M6.Adelante()

	def Parar(self):
		self.S1.setAngle(90)
		self.S3.setAngle(90)
		self.S4.setAngle(90)
		self.S6.setAngle(90)
		self.M1.Parar()
		self.M2.Parar()
		self.M3.Parar()
		self.M4.Parar()
		self.M5.Parar()
		self.M6.Parar()


#Clase motor
class Motor(object):
	#Constructor (EN1, EN2)
	def __init__(self, gpioPinIn1, gpioPinIn2):
		self.pinA = gpioPinIn1
		self.pinB = gpioPinIn2

		GPIO.setup(self.pinA, GPIO.OUT)
		GPIO.setup(self.pinB, GPIO.OUT)

	#Motor hacia adelante
	def Adelante(self):
		GPIO.output(self.pinA, True)
		GPIO.output(self.pinB, False)

	#Motor hacia atrás
	def Atras(self):
		GPIO.output(self.pinA, False)
		GPIO.output(self.pinB, True)

	#Motor parado
	def Parar(self):
		GPIO.output(self.pinA, False)
		GPIO.output(self.pinB, False)

