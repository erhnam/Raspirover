# -*- coding: utf-8 -*-

import serial
import pynmea2
import globales

def parseGPS(str):
    if str.find('GGA') > 0:
        msg = pynmea2.parse(str)
        alt  = "{:2d}".format(int(msg.latitude)) + 'º' + "{:2d}".format(int(msg.latitude_minutes)) + '′' + "{:7.4f}".format(msg.latitude_seconds) + '"'
        lon  = "{:2d}".format(int(msg.longitude)) + 'º' + "{:2d}".format(int(msg.longitude_minutes)) + '′' + "{:7.4f}".format(msg.longitude_seconds) + '"'
        data = open("locations.txt", "a")
        data.write("%s,%s\n" % ( alt, lon ))
        data.close()	
        print "altitud: ", alt
        print "longitud: ", lon

serialPort = serial.Serial("/dev/ttyAMA0", 9600, timeout=0.5)

while True:
    str = serialPort.readline()
    parseGPS(str)
