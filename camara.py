#!/usr/bin/env python3.4
# -*- encoding: utf-8 -*- 
from subprocess import call

#Funcion para empezar streaming
def camara_start():
	return_code = call("/home/pi/Raspirover/script/camara_start.sh", shell=True)

#Funcion para acabar streaming
def camara_stop():
	return_code = call("/home/pi/Raspirover/script/camara_stop.sh", shell=True)

#Funcion para hacer foto
def make_photo():
	return_code = call("/home/pi/Raspirover/script/photo.sh", shell=True)

