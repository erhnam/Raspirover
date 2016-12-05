import os
import sys

sys.path.append('/home/pi/proyecto/proyecto')

os.environ['PYTHON_EGG_CACHE'] = '/home/pi/proyecto/.python-egg'

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

