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

#Funcion para terminar streaming con base de datos
def camara_stop(arg):
	cgitb.enable()  
	os.system("/home/pi/proyecto/static/script/camara_stop.sh " + arg)

#Funcion para terminar streaming
def camara_parar():
	cgitb.enable()  
	os.system("/home/pi/proyecto/static/script/camara_parar.sh")

