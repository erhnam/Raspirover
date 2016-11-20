#!/usr/bin/python

import os

i = 155
min = 50
center = 155
max = 250

def servo_r():
        global i
        global min
        if i > min:
           i = i - 5
           os.system('echo P1-12=-5 > /dev/servoblaster')
        else:
           os.system('echo P1-12=-0 > /dev/servoblaster')

def servo_l():
        global i
        global min
        if i < max:
           i = i + 5
           os.system('echo P1-12=+5 > /dev/servoblaster')
        else:
           os.system('echo P1-12=+0 > /dev/servoblaster')

def servo_c():
        global i
        global center
        i = center
        os.system('echo P1-12=50% > /dev/servoblaster')

def servo_s():
        os.system('echo P1-12=+0 > /dev/servoblaster')

