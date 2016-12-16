#!/bin/bash
# -*- ENCODING: UTF-8 -*-

STREAMER=mjpg_streamer
RESOLUTION=640x480
FRAMERATE=25
HTTP_PORT=8554

PLUGINPATH=/usr/local/lib

LD_LIBRARY_PATH=/opt/mjpg-streamer/ /opt/mjpg-streamer/mjpg_streamer -i "input_raspicam.so -fps 25 -q 50 -vf -hf -x 640 -y 480" -o "output_http.so -p 8554 -w /opt/mjpg-streamer/www" &
