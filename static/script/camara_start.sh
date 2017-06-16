#!/bin/bash
# -*- ENCODING: UTF-8 -*-
FRAMERATE=30
HTTP_PORT=8554

LD_LIBRARY_PATH=/opt/mjpg-streamer/ /opt/mjpg-streamer/mjpg_streamer -i "input_raspicam.so -fps $FRAMERATE -q 50 -vf -hf -x 640 -y 480" -o "output_http.so -p $HTTP_PORT -w /opt/mjpg-streamer/www" &

#exec sudo wget -O /dev/shm/temp.mjpg http://192.168.0.1:8554/?action=stream &
