#!/bin/bash
#source /home/pi/proyecto/
exec sudo gunicorn -c /home/pi/proyecto/gunicorn_conf.py django_app.wsgi:application
