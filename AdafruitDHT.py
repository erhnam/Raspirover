#!/usr/bin/python

import globales
import Adafruit_DHT


pin = sys.argv[1]
sensor = Adafruit_DHT.AM2302

globales.humedad, globales.temperatura = Adafruit_DHT.read_retry(sensor, pin)
print(globales.temperatura)
