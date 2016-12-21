#!/bin/bash
# -*- ENCODING: UTF-8 -*-

FRAMERATE=24
HTTP_PORT=8080

LD_LIBRARY_PATH=/opt/mjpg-streamer/ /opt/mjpg-streamer/mjpg_streamer -i "input_raspicam.so -fps $FRAMERATE -q 50 -ex night -vf -hf -x 640 -y 480" -o "output_http.so -p $HTTP_PORT -w /opt/mjpg-streamer/www" &




