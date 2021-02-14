#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
import threading
import sys
from i2c import I2C
from sensors.BME680 import BME680, BME_680_BASEADDR
from sensors.TSL2561 import TSL2561
import time
import math
import globales
from threading import Timer

sys.path.append('./sensors')

class Singleton (type):
	_instances = {}
	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
		    cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]

class Sensors(threading.Thread, metaclass=Singleton):
	def __init__ (self, interval):
		self._timer = None
		self.interval = interval
		self.is_running = True
		self.qv_temp = None
		self.qv_humi = None
		self.qv_pressure = None
		self.qv_light = None
		self.qv_airquality = None

		self.bme680  = BME680(i2c_addr=BME_680_BASEADDR,\
	                              qv_temp=self.qv_temp, qv_humi=self.qv_humi, \
	                              qv_pressure=self.qv_pressure, qv_airquality=self.qv_airquality)

		self.tsl2561 = TSL2561(qvalue=self.qv_light)

		self.start()

	def _run(self):
		self.is_running = True
		self.start()
		self.getValues()

	def start(self):
		if self.is_running:
			self._timer = Timer(self.interval, self._run)
			self._timer.start()
			self.is_running = True

	def getValues(self):
		self.bme680.get_sensor_data()
		if self.bme680.get_sensor_data():
			print("Obteniendo dato")
			globales.temperatura = round(self.bme680.data.temperature,1)
			globales.humedad = round(self.bme680.data.humidity,1)
			globales.presion = self.bme680.data.pressure
			globales.gas = int(round(math.log(self.bme680.data.gas_resistance) + 0.04 * globales.humedad))
			print(globales.temperatura)
		globales.luz = self.tsl2561.lux()

	def stop (self):
		self._timer.cancel()
		self.is_running = False
