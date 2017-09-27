#!/usr/bin/python
import os
import time

#Inicialización de variables
i = 155
min = 50
center = 155
max = 250

def servo_lcr():
	global i
	global min
	global max
	salir = 0
	while i > min:
		servo_r()
		time.sleep(0.1)
	while i < max:
		servo_l()
		time.sleep(0.1)
	while i != center:
		if i > center:
			i = i - 5
			os.system('echo P1-11=-5 > /dev/servoblaster')
		else:
			os.system('echo P1-11=-0 > /dev/servoblaster')
		time.sleep(0.5)

#Girar servo motor a la derecha
def servo_r():
	global i
	global min
	if i > min:
		i = i - 5
		os.system('echo P1-11=-5 > /dev/servoblaster')
	else:
		os.system('echo P1-11=-0 > /dev/servoblaster')

#Girar servo motor a la izquierda
def servo_l():
	global i
	global min
	global max
	if i < max:
		i = i + 5
		os.system('echo P1-11=+5 > /dev/servoblaster')
	else:
		os.system('echo P1-11=+0 > /dev/servoblaster')

#Girar servo motor arriba
def servo_u():
	global i
	global min
	if i > min:
		i = i - 5
		os.system('echo P1-7=-5 > /dev/servoblaster')
	else:
		os.system('echo P1-7=-0 > /dev/servoblaster')

#Girar servo motor a la abajo
def servo_d():
	global i
	global min
	global max
	if i < max:
		i = i + 5
		os.system('echo P1-7=+5 > /dev/servoblaster')
	else:
		os.system('echo P1-7=+0 > /dev/servoblaster')

#Situar el servo en el centro
def servo_c():
        global i
        global center
        i = center
        os.system('echo P1-11=50% > /dev/servoblaster')
        os.system('echo P1-7=50% > /dev/servoblaster')

#Para el servo
def servo_s():
        os.system('echo P1-11=+0 > /dev/servoblaster')
