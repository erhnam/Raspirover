import serial
import pynmea2
import globales

def parseGPS(str):
    if str.find('GGA') > 0:
        msg = pynmea2.parse(str)
	globales.hora = msg.timestamp
	globales.latitud = msg.lat + ' ' + msg.lat_dir
	globales.longitud = msg.lon + ' ' + msg.lon_dir
	globales.altura = "{:.1f}".format(msg.altitude) + ' ' + msg.altitude_units
	print 'hora: ', globales.hora
	print 'latitud: ', globales.latitud
	print 'longitud: ', globales.longitud
	print 'altura: ', globales.altura
	data = open("locations.txt", "a")
	data.write("%s,%s\n" % (msg.lat, msg.lon))
	data.close()	

serialPort = serial.Serial("/dev/ttyAMA0", 9600, timeout=0.5)

while True:
    str = serialPort.readline()
    parseGPS(str)
