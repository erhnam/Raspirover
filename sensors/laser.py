#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO

class Laser(object):
	def __init__ (self, laserpin):
		self.laserpin = laserpin

	def setup(self):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.laserpin, GPIO.OUT)
		GPIO.output(self.laserpin, GPIO.LOW)

	def on(self):
		GPIO.output(self.laserpin, GPIO.HIGH) # led on

	def off(self):
		GPIO.output(self.laserpin, GPIO.LOW) # led off

	def destroy():
		GPIO.output(LaserGPIO, GPIO.LOW)
		GPIO.cleanup()
