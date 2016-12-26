#!/usr/bin/python
import os

#Inicialización de variables
i = 155
min = 50
center = 155
max = 250

#Girar servo motor a la derecha
def servo_r():
        global i
        global min
        if i > min:
           i = i - 5
           os.system('echo P1-12=-5 > /dev/servoblaster')
        else:
           os.system('echo P1-12=-0 > /dev/servoblaster')

#Girar servo motor a la izquierda
def servo_l():
        global i
        global min
        if i < max:
           i = i + 5
           os.system('echo P1-12=+5 > /dev/servoblaster')
        else:
           os.system('echo P1-12=+0 > /dev/servoblaster')

#Situar el servo en el centro
def servo_c():
        global i
        global center
        i = center
        os.system('echo P1-12=50% > /dev/servoblaster')

#Para el servo
def servo_s():
        os.system('echo P1-12=+0 > /dev/servoblaster')
