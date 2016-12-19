#!/usr/bin/env python3
# -*- encoding: utf-8 -*- 
from subprocess import call
import os
from cgi import escape
import cgitb
#Funcion para empezar streaming
def camara_start():
	cgitb.enable()  
	os.system("/home/pi/proyecto/static/script/camara_start.sh")
#	return_code = call("/usr/lib/cgi-bin/camara_start.sh", shell=True)

#	a="sudo LD_LIBRARY_PATH=/opt/mjpg-streamer/ /opt/mjpg-streamer/mjpg_streamer -i "	
#	b= "'input_raspicam.so -fps 24 -q 50 -ex night -vf -hf -x 640 -y 480'"
#	c= " -o 'output_http.so -p 8554 -w /opt/mjpg-streamer/www' & "
#	d= a+b+c
#	os.system(d)

#Funcion para terminar streaming
def camara_stop():
	os.system("/home/pi/proyecto/static/script/camara_stop.sh")
#	return_code = call("/home/pi/proyecto/static/script/camara_stop.sh", shell=True)
#	return_code = call("/usr/lib/cgi-bin/camara_stop.sh", shell=True)
#	a= "sudo kill -9 `pidof mjpg_streamer`"
#	os.system(a)



