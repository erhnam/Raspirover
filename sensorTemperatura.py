import time
import RPi.GPIO as GPIO
import globales
import re
import subprocess
	
def comprobarth():
	
	adafruit = "/home/pi/Raspirover/AdafruitDHT.py"

	sensorReadings = subprocess.check_output(['sudo', adafruit, '2302', '14'])

	temperatura = 0	
	temperature = re.findall(r"Temp=(\d+.\d+)", sensorReadings)[0]

	#humidity = re.findall(r"Humidity=(\d+.\d+)", sensorReadings)[0]
	#intHumidity = float(humidity)
	intTemp = float(temperature)

	return intTemp, intHumidity

