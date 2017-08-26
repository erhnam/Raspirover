#!/usr/bin/env python3
# -*- encoding: utf-8 -*- 
import os
import subprocess

#Funcion para empezar streaming
def camara_start():
	#os.system("/home/pi/proyecto/static/script/camara_start.sh")
	subprocess.Popen(["/home/pi/Raspirover/static/script/camara_start.sh"], stdin=subprocess.PIPE)

#Funcion para terminar streaming
def camara_parar():
	#os.system("/home/pi/proyecto/static/script/camara_parar.sh")
	subprocess.Popen(["/home/pi/Raspirover/static/script/camara_parar.sh"], stdin=subprocess.PIPE)

