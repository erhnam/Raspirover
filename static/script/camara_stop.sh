#!/bin/bash
# -*- ENCODING: UTF-8 -*-
#Comprobación de linea argumentos

if [ $# -lt 1 ]; #Si el número de argumentos es menor que 1...
then
    echo "Error de sintaxis. $0 <nombre del video>"
    exit 1
fi

sudo kill -9 `pidof mjpg_streamer`

sudo ffmpeg -i /dev/shm/temp.mjpg /home/pi/proyecto/media/videos/$1.mp4

sudo rm -rf /dev/shm/temp.mjpg
