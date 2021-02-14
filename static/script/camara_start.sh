#!/bin/bash
# -*- ENCODING: UTF-8 -*-

FRAMERATE=24
HTTP_PORT=8554

LD_LIBRARY_PATH=/usr/local/bin/ /usr/local/bin/mjpg_streamer -i "input_raspicam.so -fps $FRAMERATE -q 50 -vf -hf -x 640 -y 480" -o "output_http.so -p $HTTP_PORT -w /opt/mjpg-streamer/www" &
