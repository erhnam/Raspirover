import RPi.GPIO as GPIO    #Importamos la libreria RPi.GPIO
import time                #Importamos time para poder usar time.sleep

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)   #Ponemos la Raspberry en modo BCM

class Servo(object):
	def __init__(self,pin):
		self.PIN = pin
		self.VAR = 0.3
		self.MAX = 10.5
		self.MIN = 4.5
		self.CENTER = 7.5
		self.POS = 7.5
		GPIO.setup(self.PIN,GPIO.OUT)
		self.servo = GPIO.PWM(self.PIN,50)
		self.servo.start(self.POS)

	def stop(self):
		self.servo.stop()

	def right(self):
		if self.POS > self.MIN:
			print("right")
			self.POS = round(self.POS - self.VAR,1)
			self.servo.start(self.POS)
			self.servo.ChangeDutyCycle(self.POS)    

	def left(self):
		if self.POS < self.MAX:
			print("left")
			self.POS = round(self.POS + self.VAR,1)
			print(self.POS)
			self.servo.start(self.POS)
			self.servo.ChangeDutyCycle(self.POS)

	def up(self):
		if self.POS > self.MIN:
			self.POS = self.POS - self.VAR
			self.servo.ChangeDutyCycle(self.POS)

	def down(self):
		if self.POS < self.MAX:
			self.POS = self.POS + self.VAR
			self.servo.ChangeDutyCycle(self.POS)

	def center(self):
		self.POS = self.CENTER
		self.servo.ChangeDutyCycle(self.POS)
