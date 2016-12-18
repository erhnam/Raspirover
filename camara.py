#!/usr/bin/env python3.4
# -*- encoding: utf-8 -*- 
from subprocess import call
import os

#Funcion para empezar streaming
def camara_start():
	return_code = call("/home/pi/proyecto/static/script/camara_start.sh", shell=True)

#Funcion para terminar streaming
def camara_stop():
	return_code = call("/home/pi/proyecto/static/script/camara_stop.sh", shell=True)

