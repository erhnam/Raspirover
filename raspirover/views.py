# -*- encoding: utf-8 -*-
########################## LIBRERÍAS ###############################
from django.utils import timezone
from django.db import transaction
#para graficas Chartit2
from chartit import DataPool, Chart
#Para django_extensions
import django_extensions
#Renders de Django
from django.shortcuts import render, redirect, render_to_response
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
#Clase User de Django
from django.contrib.auth.models import User
#Para obligar a estar logueado en sistema
from django.contrib.auth.decorators import login_required  
from django.contrib import auth, messages
#Para autintificar, el login y el logout
from django.contrib.auth import authenticate, login, logout
#para password                                                     
from django.contrib.auth.hashers import make_password
#Para crear contextos       
from django.template import Context, RequestContext
#Librería asyncio para operaciones asincronas
import asyncio
#Librería time
import time
from datetime import datetime
#Librería para controlar GPIO
import RPi.GPIO as GPIO
#Libreria para hilos
import threading
#Libreria para Max, min y avg
from django.db.models import Avg, Max, Min

#Importaciones de ficheros creados para sensores, camara, motores y globales.
from .models import *
from .forms import *
from servo import *
from motor import *
from camara import *
from driver import *
from globales import * 
from timer import *
from sensors import *


########################## PINES GPIO ##########################

DTH22 = 2
LEDIZQ = 16
LEDDER = 20
SFSR02 = 23
MOTORIN1 = 6  
MOTORIN2 = 5
MOTORENA = 13
MOTORIN3 = 27 
MOTORIN4 = 22
MOTORENB = 12
SERVOHOR = 18 
SERVOVER = 21

########################## CANAL SPI ##########################

SENSORFUEGO = 0 
SENSORGAS = 7
SENSORLUZ = 6

########################## MANAGER DE TAREAS ##########################

scheduler = Scheduler()

########################## VOLTAJE ##########################

spi = SPI(canalGas = SENSORGAS, canalLuz = SENSORLUZ, canalFuego = SENSORFUEGO)

#bateria = Task( 59.0 , spi.ObtenerBateria )
#bateria.start_timer()

#Creacion de los motores por parejas
MOTORDER = Motor (MOTORIN2,MOTORIN1)
MOTORIZQ = Motor (MOTORIN3,MOTORIN4)

#Creacion del driver L298N
driver = DriverDosMotores (MOTORIZQ, MOTORDER)

#Creacion de los Servos
#servoHor = Servo(SERVOHOR)
#servoVer = Servo(SERVOVER)

########################## INICIO  ###############################

#funcion para apagar el sistema
def apagar(request):
	os.system("sudo shutdown -h now")	

#funcion para reiniciar el sistema
def reboot(request):
	os.system("sudo reboot")	

def inicializar(request):

	request.session['stemp'] = False
	request.session['shum'] = False	
	request.session['sgas'] = False
	request.session['sfuego'] = False
	request.session['sluz'] = False	
	request.session['sgps'] = False
	request.session['camara'] = False
	request.session['tiempo'] = False
	request.session['salir'] = False
	request.session['dbexplo'] = None

#Función de la página principal del programa
def index(request):

#	global servoHor
#	global servoVer
	salir(request)

	inicializar(request)

	#Centra la camara
#	servoHor.center()
#	servoVer.center()

	servo_c()

	#Se inicializa los puertos GPIO
	#setup(DTH22,LEDIZQ,LEDDER,SFSR02,MOTORIN1,MOTORIN2,MOTORENA,MOTORIN3,MOTORIN4,MOTORENB)
	#setup(DTH22,LEDIZQ,LEDDER,SFSR02)
	setup(14,21,20,16,26,22,27,5,6,12,23)

	return render(request, 'index.html')

#Funcion que accede a la página Analizar
@login_required(login_url='/')
def analizar(request):
	request.session['salir']=True

	#extraer todas las exploraciones del usuario
	explo=Exploracion.objects.filter(usuariofk=request.user)

	return render(request, 'analizar.html', {'explo': explo})

#Funcion que ofrece las opciones para iniciar una exploración
@login_required(login_url='/')
def explorar(request):

	global scheduler

	#Si es método post
	if request.method == "POST":
		#se crea un formulaio
		form = ExploracionForm(request.POST)
		#Si el formulario es válido
		if form.is_valid():
			#Se extraen los valores del formulario
			cleaned_data = form.cleaned_data
			request.session['stemp']  = cleaned_data.get('temperatura')
			request.session['shum']   = cleaned_data.get('humedad')
			request.session['sgas']   = cleaned_data.get('gas')
			request.session['sfuego'] = cleaned_data.get('fuego')
			request.session['sluz']   = cleaned_data.get('luz')	
			request.session['sgps']   = cleaned_data.get('gps')
			request.session['camara'] = cleaned_data.get('camara')
			request.session['tiempo'] = cleaned_data.get('tiempo')
			nombre = cleaned_data.get('nombre')
			descripcion = cleaned_data.get('descripcion')
	
			#Se crea una exploracion con parte de los valores del formulario
			#Si tiempo no está vacío se crea una exploracion	
			if request.session['tiempo'] is not None:
				request.session['tiempo'] = float(request.session['tiempo'])
				dbexplo = Exploracion(nombre=nombre, tiempo=request.session['tiempo'], usuariofk=request.user, descripcion=descripcion)
				dbexplo.save()
				request.session['dbexplo'] = dbexplo.id_exploracion	

			#Se ha elegido en el formulario el sensor de temperatura o humedad (es el mismo)			
			if request.session['stemp']  == True or request.session['shum'] == True:
				#Se crea una tabla sensor de temperatura asociado a la exploracion
				if request.session['stemp'] == True and request.session['tiempo'] is not None:
					dbtemperatura = Sensor(tipo="Temperatura", enable=True)
					dbtemperatura.save()
					dbexplo.sensores.add(dbtemperatura)
	
				#Se crea una tabla sensor de humedad asociada a la exploracion	
				if request.session['shum'] == True and request.session['tiempo'] is not None:
					dbhumedad = Sensor(tipo="Humedad", enable=True)
					dbhumedad.save()
					dbexplo.sensores.add(dbhumedad)

				#Si el tiempo es null se ejecuta el sensor cada 1 segundo			
				if request.session['tiempo'] is None:	
					scheduler.AddTask( 1.0 , comprobarth )

				#Si el tiempo no es null se crea un timer de x segundos definidos por la variable tiempo
				else:
					scheduler.AddTask( request.session['tiempo'], comprobarth )

			#Se ha elegido en el formulario el sensor de luz		
			if request.session['sluz'] == True:
				#Se crea un timer de x segundos definidos por la variable tiempo
				if request.session['tiempo'] is not None:	
					#Se crea una tabla sensor de luz asociada a la exploracion	
					dbluz = Sensor(tipo="Luz", enable=True)
					dbluz.save()
					dbexplo.sensores.add(dbluz)
					#Se crea un timer de x segundos definidos por la variable tiempo
					scheduler.AddTask( request.session['tiempo'], spi.ObtenerLuz)

				#Si el tiempo es null se ejecuta el sensor cada 5 segundos	
				else:
					#Se crea un timer de 1 segundo
					scheduler.AddTask( 1.0 , spi.ObtenerLuz)

			#Se ha elegido en el formulario el sensor de gas
			if request.session['sgas'] == True:
				#Si el tiempo no es null se ejecuta el sensor segun tiempo asignado	
				if request.session['tiempo'] is not None:
					#Se crea una tabla sensor de gas asociada a la exploracion	
					dbgas = Sensor(tipo="Gas", enable=True)
					dbgas.save()
					dbexplo.sensores.add(dbgas)
					dbgas = Sensor(tipo="Co", enable=True)
					dbgas.save()
					dbexplo.sensores.add(dbgas)
					dbgas = Sensor(tipo="Humo", enable=True)
					dbgas.save()
					dbexplo.sensores.add(dbgas)
					#Se crea un timer de x segundos definidos por la variable tiempo
					scheduler.AddTask( request.session['tiempo'] , spi.ObtenerGas)

				#Si el tiempo es null se ejecuta el sensor cada 5 segundos			
				else:
					#Se crea un timer de 1 segundo
					scheduler.AddTask( 1.0 , spi.ObtenerGas)

			#Se ha elegido en el formulario el sensor de fuego
			if request.session['sfuego'] == True:
				#Si el tiempo no es null se ejecuta el sensor segun tiempo asignado	
				if request.session['tiempo'] is not None:
					#Se crea una tabla sensor de gas asociada a la exploracion	
					dbfuego = Sensor(tipo="Fuego", enable=True)
					dbfuego.save()
					dbexplo.sensores.add(dbfuego)
					#Se crea un timer de x segundos definidos por la variable tiempo
					scheduler.AddTask( request.session['tiempo'] , spi.ObtenerFuego)

				#Si el tiempo es null se ejecuta el sensor cada 5 segundos			
				else:
					#Se crea un timer de 1 segundo
					scheduler.AddTask( 1.0 , spi.ObtenerFuego)

			#Se ha elegido en el formulario el sensor de gas
			if request.session['sgps'] == True:
				gps = GPS()
				#Si el tiempo no es null se ejecuta el sensor segun tiempo asignado	
				if request.session['tiempo'] is not None:
					#Se crea una tabla sensor de gas asociada a la exploracion	
					dbgps = Sensor(tipo="Gps", enable=True)
					dbgps.save()
					dbexplo.sensores.add(dbgps)
					#Se crea un timer de x segundos definidos por la variable tiempo
					scheduler.AddTask( request.session['tiempo'] , gps.leer )

				#Si el tiempo es null se ejecuta el sensor cada 5 segundos			
				else:
					#Se crea un timer de 1 segundo
					scheduler.AddTask( 1.0 , gps.leer)


			#Si se ha elegido cámara para streaming
			if request.session['camara'] == True:
				camara_start()

			#Si se ha insertado tiempo se lanza un trigger para la bbdd
			#definida por la variable tiempo
			if request.session['tiempo'] is not None:
				scheduler.AddTask( (request.session['tiempo']), BBDD, args=[request, dbexplo.id_exploracion] )

			#Si se ha elegido manual
			if request.method=='POST' and 'manual' in request.POST:				
				#Ejecucion Manual sin sensores	
				if request.session['stemp'] == False and request.session['shum'] == False and request.session['sgas'] == False and request.session['sluz'] == False:
					return redirect('manual')
				#Activa todos los sensores asignados
				else:
					scheduler.StartAllTasks()
					return redirect('manual')

			#si se ha elegido automatico
			if request.method=='POST' and 'automatico' in request.POST:
				#Ejecucion Automatica sin sensores	
				if request.session['stemp'] == False and request.session['shum'] == False and request.session['sgas'] == False and request.session['sluz'] == False:
					return redirect('auto')
				#Activa todos los sensores asignados
				else:
					scheduler.StartAllTasks()
					return redirect('auto')

	else:
		form = ExploracionForm()

	context = {'form': form}

	return render(request, 'explorar.html', context)

#Funcion que guarda valores de sensores en la base de datos
#@transaction.atomic
#@transaction.commit_manually
def BBDD(request, id_exploracion):

	sta = datetime.now()
	start = timezone.now()

	#Se busca la exploracion actual
	explo = Exploracion.objects.get(pk=id_exploracion)
	#Se obtienen los sensores utilizados en la exploración
	sensores = Sensor.objects.filter(exploracion=explo)

	with transaction.atomic():
		for sensor in sensores:
			if sensor.tipo == "Luz":
				valor = Lecturas.objects.create(dato=globales.luz, fecha=start, sensor=sensor)

			elif sensor.tipo == "Gas":
				valor = Lecturas.objects.create(dato=globales.gas, fecha=start, sensor=sensor)

			elif sensor.tipo == "Co":
				valor = Lecturas.objects.create(dato=globales.co, fecha=start, sensor=sensor)

			elif sensor.tipo == "Humo":
				valor = Lecturas.objects.create(dato=globales.smoke, fecha=start, sensor=sensor)

			elif sensor.tipo == "Fuego":
				valor = Lecturas.objects.create(dato=globales.fuego, fecha=start, sensor=sensor)

			elif sensor.tipo == "Temperatura":
				valor = Lecturas.objects.create(dato=globales.temperatura, fecha=start, sensor=sensor)

			elif sensor.tipo == "Humedad":
				valor = Lecturas.objects.create(dato=globales.humedad, fecha=start, sensor=sensor)

			elif sensor.tipo == "Gps":
				valor = Lecturas.objects.create(dato=(globales.luz+"-"+globales.lon), fecha=start, sensor=sensor)

	end = datetime.now()
	diff = end - sta
	elapsed_ms = (diff.days * 86400000) + (diff.seconds * 1000) + (diff.microseconds / 1000)
	print(elapsed_ms)

			
#Elimina una exploración elegida por el usuario
@login_required(login_url='/')
def eliminarExploracion(request, id_exploracion):
	#Se busca la exploracion actual
	explo = Exploracion.objects.get(pk=id_exploracion)
	#Se busca los sensores utilizados en la exploracion
	sensores = Sensor.objects.filter(exploracion=explo)

	with transaction.atomic():

		#Se eliminan los sensores y tambien los datos
		for sensor in sensores:
			if sensor.tipo == "Luz":
				s = Sensor.objects.get(exploracion=explo, tipo="Luz")
				s.delete()
				sensor.delete()

			elif sensor.tipo == "Gas":
				s = Sensor.objects.get(exploracion=explo, tipo="Gas")
				s.delete()
				sensor.delete()

			elif sensor.tipo == "Fuego":
				s = Sensor.objects.get(exploracion=explo, tipo="Fuego")
				s.delete()
				sensor.delete()

			elif sensor.tipo == "Temperatura":
				s = Sensor.objects.get(exploracion=explo, tipo="Temperatura")
				s.delete()
				sensor.delete()

			elif sensor.tipo == "Humedad":
				s = Sensor.objects.get(exploracion=explo, tipo="Humedad")
				s.delete()
				sensor.delete()

			elif sensor.tipo == "Gps":
				s = Sensor.objects.get(exploracion=explo, tipo="Gps")
				s.delete()
				sensor.delete()

		#elimina la exploracion de la base de datos
		explo.delete()

	#vuelve a la pagina de analisis
	return redirect('analizar')

#Funcion que muestra detalles de una exploracion elegida por usuario
def detallesExploracion (request, id_exploracion):
	#variables para la página
	t = "Temperatura"
	h = "Humedad"
	l = "Luz"
	g = "Gas"
	c = "Co"
	s = "Humo"
	f = "Fuego"
	gp = "Gps"

	#extraer solo la exploracion seleccionada
	explo = Exploracion.objects.get(pk=id_exploracion)
	#extraer los sensores utilizados en la exploracion
	sensores = Sensor.objects.filter(exploracion=explo)

	context = {'explo':explo, 't':t, 'h':h, 'l':l, 'g':g, 'f':f, 'gps': gp, 's':s, 'c':c, 'sensores' : sensores }

	return render(request, 'detalleExploracion.html', context)

#Funcion que muestra una gráfica seleccionada
@login_required(login_url='/')
def mostrarMapa (request, id_exploracion):
	#con sensor_tipo se sabe la gráfica que se ha seleccionado
	explo = Exploracion.objects.get(pk=id_exploracion)

	gps = sensorGps.objects.get(exploracion=explo)

	coords = sensorDatoUart.objects.filter(sensorgps = gps)
 
	lats = []
	lons = []

	for i in coords:
		if i.lat != None and i.lon != None:
			lats.append(i.lat)
			lons.append(i.lon)

	context = {'coords': coords, 'explo' : explo , 'lats' : lats, 'lons' : lons}

	return render(request, 'mostrarMapa.html', context)

#Funcion que muestra una gráfica seleccionada
@login_required(login_url='/')
def mostrarGrafica (request, id_exploracion, sensor_tipo):
	#con sensor_tipo se sabe la gráfica que se ha seleccionado
	explo = Exploracion.objects.get(pk=id_exploracion)

	if sensor_tipo == "Temperatura":
		
		titulo = "Gráfica de la exploracion " + explo.nombre + " de Temperatura" 

		sensor =  Sensor.objects.get(exploracion=explo, tipo="Temperatura")

		lecturas = Lecturas.objects.filter(sensor=sensor)

		min = lecturas.all().aggregate(Min('dato')).get('dato__min', 0)
		max = lecturas.all().aggregate(Max('dato')).get('dato__max', 0)
		avg = round(lecturas.all().aggregate(Avg('dato')).get('dato__avg', 0.00),2)

		#paso 1: Crear el datapool con los datos que queremos recibir.
		data = \
			DataPool(
			   series=
				[{'options': {
				   'source': lecturas.all()},
				  'terms': [
					('fecha',lambda d: d.strftime("%H:%M:%S") ),
					('dato',lambda e: float(e))]}
				 ])

		#paso 2: Crear la gráfica
		cht = Chart(
				datasource = data,
				series_options =
				  [{'options':{
					  'type': 'line',
					  'stacking': False},
					'terms':{
					  'fecha': [
						'dato']
					  }}],
				chart_options={
					'title': {
						'text': titulo},
					'xAxis': {
						'title': {
							'text': 'Tiempo'}},
					'yAxis': {
						'title': {
							'text': 'Temperatura'}},
					'legend': {
						'enabled': False},
					'credits': {
						'enabled': False}})

		#paso 3: Enviar la gráfica a la página.
		context = {'sensor':sensor, 'chart': cht, 'tipo': sensor_tipo ,'explo' : explo, 'min' : min , 'max' : max , 'avg' : avg }

		return render(request, 'mostrarGrafica.html', context)

	#Se ha seleccionado gráfica de humedad
	elif sensor_tipo == "Humedad":

		titulo = "Gráfica de la exploracion " + explo.nombre + " de Humedad" 

		sensor =  Sensor.objects.get(exploracion=explo, tipo="Humedad")

		lecturas = Lecturas.objects.filter(sensor=sensor)

		min = lecturas.all().aggregate(Min('dato')).get('dato__min', 0)
		max = lecturas.all().aggregate(Max('dato')).get('dato__max', 0)
		avg = round(lecturas.all().aggregate(Avg('dato')).get('dato__avg', 0.00),2)

		#paso 1: Crear el datapool con los datos que queremos recibir.
		data = \
			DataPool(
			   series=
				[{'options': {
				   'source': lecturas.all()},
				  'terms': [
					('fecha',lambda d: d.strftime("%H:%M:%S") ),
					('dato',lambda e: float(e))]}
				 ])

		#paso 2: Crear la gráfica
		cht = Chart(
				datasource = data,
				series_options =
				  [{'options':{
					  'type': 'line',
					  'stacking': False},
					'terms':{
					  'fecha': [
						'dato']
					  }}],
				chart_options={
					'title': {
						'text': titulo},
					'xAxis': {
						'title': {
							'text': 'Tiempo'}},
					'yAxis': {
						'title': {
							'text': 'Humedad'}},
					'legend': {
						'enabled': False},
					'credits': {
						'enabled': False}})

		#paso 3: Enviar la gráfica a la página.
		context = {'sensor':sensor, 'chart': cht, 'tipo': sensor_tipo ,'explo' : explo, 'min' : min , 'max' : max , 'avg' : avg }

		return render(request, 'mostrarGrafica.html', context)

	#Se ha seleccionado gráfica de Gas
	elif sensor_tipo == "Gas":

		titulo = "Gráfica de la exploracion " + explo.nombre + " de Gas" 

		sensor =  Sensor.objects.get(exploracion=explo, tipo="Gas")

		lecturas = Lecturas.objects.filter(sensor=sensor)

		min = lecturas.all().aggregate(Min('dato')).get('dato__min', 0)
		max = lecturas.all().aggregate(Max('dato')).get('dato__max', 0)
		avg = round(lecturas.all().aggregate(Avg('dato')).get('dato__avg', 0.00),2)

		#paso 1: Crear el datapool con los datos que queremos recibir.
		data = \
			DataPool(
			   series=
				[{'options': {
				   'source': lecturas.all()},
				  'terms': [
					('fecha',lambda d: d.strftime("%H:%M:%S") ),
					('dato',lambda e: int(e))]}
				 ])

		#paso 2: Crear la gráfica
		cht = Chart(
				datasource = data,
				series_options =
				  [{'options':{
					  'type': 'line',
					  'stacking': False},
					'terms':{
					  'fecha': [
						'dato']
					  }}],
				chart_options={
					'title': {
						'text': titulo},
					'xAxis': {
						'title': {
							'text': 'Tiempo'}},
					'yAxis': {
						'title': {
							'text': 'Gas'}},
					'legend': {
						'enabled': False},
					'credits': {
						'enabled': False}})

		#paso 3: Enviar la gráfica a la página.
		context = {'sensor':sensor, 'chart': cht, 'tipo': sensor_tipo ,'explo' : explo, 'min' : min , 'max' : max , 'avg' : avg }

		return render(request, 'mostrarGrafica.html', context)

	elif sensor_tipo == "Co":

		titulo = "Gráfica de la exploracion " + explo.nombre + " de Co" 

		sensor =  Sensor.objects.get(exploracion=explo, tipo="Co")

		lecturas = Lecturas.objects.filter(sensor=sensor)

		min = lecturas.all().aggregate(Min('dato')).get('dato__min', 0)
		max = lecturas.all().aggregate(Max('dato')).get('dato__max', 0)
		avg = round(lecturas.all().aggregate(Avg('dato')).get('dato__avg', 0.00),2)

		#paso 1: Crear el datapool con los datos que queremos recibir.
		data = \
			DataPool(
			   series=
				[{'options': {
				   'source': lecturas.all()},
				  'terms': [
					('fecha',lambda d: d.strftime("%H:%M:%S") ),
					('dato',lambda e: int(e))]}
				 ])

		#paso 2: Crear la gráfica
		cht = Chart(
				datasource = data,
				series_options =
				  [{'options':{
					  'type': 'line',
					  'stacking': False},
					'terms':{
					  'fecha': [
						'dato']
					  }}],
				chart_options={
					'title': {
						'text': titulo},
					'xAxis': {
						'title': {
							'text': 'Tiempo'}},
					'yAxis': {
						'title': {
							'text': 'CO'}},
					'legend': {
						'enabled': False},
					'credits': {
						'enabled': False}})

		#paso 3: Enviar la gráfica a la página.
		context = {'sensor':sensor, 'chart': cht, 'tipo': sensor_tipo ,'explo' : explo, 'min' : min , 'max' : max , 'avg' : avg }

		return render(request, 'mostrarGrafica.html', context)

	elif sensor_tipo == "Humo":

		titulo = "Gráfica de la exploracion " + explo.nombre + " de Humo" 

		sensor =  Sensor.objects.get(exploracion=explo, tipo="Humo")

		lecturas = Lecturas.objects.filter(sensor=sensor)

		min = lecturas.all().aggregate(Min('dato')).get('dato__min', 0)
		max = lecturas.all().aggregate(Max('dato')).get('dato__max', 0)
		avg = round(lecturas.all().aggregate(Avg('dato')).get('dato__avg', 0.00),2)

		#paso 1: Crear el datapool con los datos que queremos recibir.
		data = \
			DataPool(
			   series=
				[{'options': {
				   'source': lecturas.all()},
				  'terms': [
					('fecha',lambda d: d.strftime("%H:%M:%S") ),
					('dato',lambda e: int(e))]}
				 ])

		#paso 2: Crear la gráfica
		cht = Chart(
				datasource = data,
				series_options =
				  [{'options':{
					  'type': 'line',
					  'stacking': False},
					'terms':{
					  'fecha': [
						'dato']
					  }}],
				chart_options={
					'title': {
						'text': titulo},
					'xAxis': {
						'title': {
							'text': 'Tiempo'}},
					'yAxis': {
						'title': {
							'text': 'Humo'}},
					'legend': {
						'enabled': False},
					'credits': {
						'enabled': False}})

		#paso 3: Enviar la gráfica a la página.
		context = {'sensor':sensor, 'chart': cht, 'tipo': sensor_tipo ,'explo' : explo, 'min' : min , 'max' : max , 'avg' : avg }

		return render(request, 'mostrarGrafica.html', context)

	#Se ha seleccionado gráfica de Fuego
	elif sensor_tipo == "Fuego":

		titulo = "Gráfica de la exploracion " + explo.nombre + " de Fuego" 

		sensor =  Sensor.objects.get(exploracion=explo, tipo="Fuego")

		lecturas = Lecturas.objects.filter(sensor=sensor)

		min = lecturas.all().aggregate(Min('dato')).get('dato__min', 0)
		max = lecturas.all().aggregate(Max('dato')).get('dato__max', 0)
		avg = round(lecturas.all().aggregate(Avg('dato')).get('dato__avg', 0.00),2)

		#paso 1: Crear el datapool con los datos que queremos recibir.
		data = \
			DataPool(
			   series=
				[{'options': {
				   'source': lecturas.all()},
				  'terms': [
					('fecha',lambda d: d.strftime("%H:%M:%S") ),
					('dato',lambda e: int(e))]}
				 ])

		#paso 2: Crear la gráfica
		cht = Chart(
				datasource = data,
				series_options =
				  [{'options':{
					  'type': 'line',
					  'stacking': False},
					'terms':{
					  'fecha': [
						'dato']
					  }}],
				chart_options={
					'title': {
						'text': titulo},
					'xAxis': {
						'title': {
							'text': 'Tiempo'}},
					'yAxis': {
						'title': {
							'text': 'Fuego'}},
					'legend': {
						'enabled': False},
					'credits': {
						'enabled': False}})

		#paso 3: Enviar la gráfica a la página.
		context = {'sensor':sensor, 'chart': cht, 'tipo': sensor_tipo ,'explo' : explo, 'min' : min , 'max' : max , 'avg' : avg }

		return render(request, 'mostrarGrafica.html', context)


	#Se ha seleccionado gráfica de Luz
	elif sensor_tipo == "Luz":

		titulo = "Gráfica de la exploracion " + explo.nombre + " de Luz" 

		sensor =  Sensor.objects.get(exploracion=explo, tipo="Luz")

		lecturas = Lecturas.objects.filter(sensor=sensor)

		min = lecturas.all().aggregate(Min('dato')).get('dato__min', 0)
		max = lecturas.all().aggregate(Max('dato')).get('dato__max', 0)
		avg = round(lecturas.all().aggregate(Avg('dato')).get('dato__avg', 0.00),2)

		#paso 1: Crear el datapool con los datos que queremos recibir.
		data = \
			DataPool(
			   series=
				[{'options': {
				   'source': lecturas.all()},
				  'terms': [
					('fecha',lambda d: d.strftime("%H:%M:%S") ),
					('dato',lambda e: int(e))]}
				 ])

		#paso 2: Crear la gráfica
		cht = Chart(
				datasource = data,
				series_options =
				  [{'options':{
					  'type': 'line',
					  'stacking': False},
					'terms':{
					  'fecha': [
						'dato']
					  }}],
				chart_options={
					'title': {
						'text': titulo},
					'xAxis': {
						'title': {
							'text': 'Tiempo'}},
					'yAxis': {
						'title': {
							'text': 'Lx'}},
					'legend': {
						'enabled': False},
					'credits': {
						'enabled': False}})

		#paso 3: Enviar la gráfica a la página.
		context = {'sensor':sensor, 'chart': cht, 'tipo': sensor_tipo ,'explo' : explo, 'min' : min , 'max' : max , 'avg' : avg }

		return render(request, 'mostrarGrafica.html', context)

#Funcion para salir del modo de control
@login_required(login_url='/')
def salir(request):

	global scheduler

	#Destruye los timers
	request.session['salir'] = True

	#Para el Manager del sistema
	scheduler.StopAllTasks()

	#Para la camara
	camara_parar()

	#si estaba en automático
	if globales.auto == True:
		print("Eliminando sesion Auto\n")
		#borra hilo de automático
		globales.auto = False
		#globales.automatic.join()
		del globales.automatic
		globales.automatic = None

	request.session['salir'] = False

	#Inicializacion de variables
	globales.inicializar()


	#redirige al index
	return redirect('index')

#Función que muestra el porcentaje del voltaje de la pila
#En la pantalla de control del sistema
@login_required(login_url='/')
def mostrarvoltaje(request):

	context = {'voltaje': globales.porcentaje}

	template = "base.html"
	return render(request, template, context)

#Función que muestra los datos de los sensores en pantalla modo de control
#En la pantalla de control del sistema
@login_required(login_url='/')
def mostrardatos(request):

	context = {'temperatura': globales.temperatura, 'humedad': globales.humedad, 
	'gas' : globales.gas, 'luz' : globales.luz, 'fuego' : globales.fuego,
	'stemp' : request.session['stemp'], 'shum' : request.session['shum'], 
	'sgas' : request.session['sgas'], 'sfuego' : request.session['sfuego'], 
	'sluz' : request.session['sluz'], 'camara' : request.session['camara']}

	template = "datos.html"
	return render(request, template, context)

#Funcion para girar a la derecha en asincrono
def Derecha():
	global driver
	eventloop = asyncio.new_event_loop()
	asyncio.set_event_loop(eventloop)
	eventloop.run_until_complete(driver.GirarDerAsync()) 
	eventloop.close()

#Funcion para girar a la izquierda en asincrono
def Izquierda():
	global driver
	eventloop = asyncio.new_event_loop()
	asyncio.set_event_loop(eventloop)
	eventloop.run_until_complete(driver.GirarIzqAsync()) 
	eventloop.close()

#Función de control manual del sistema
@login_required(login_url='/')
def manual(request):
	global driver
#	global servoHor
#	global servoVer

	#Se recoge la peticion de wmovimiento
	if 'cmd' in request.GET and request.GET['cmd']:
		control = request.GET['cmd']

		#Control de la direccion
		#Mover hacia adelante
		if (control == "fwd"):
			driver.Adelante()
		#Mover hacia atras
		elif (control == "bwd"):
			driver.Atras()
		#Mover a la izquierda
		elif (control == "left"):
			driver.Izquierda()
		#Mover a la derecha
		elif (control == "right"):
			driver.Derecha()
		#Parar los motores		
		elif (control == "stop"):
			driver.Parar()  	
		#Aumentar velocidad
		elif (control == "sup"):
			globales.velocidad = globales.velocidad + 10
			driver.SetSpeed(globales.velocidad)
		#Disminuir velocidad	
		elif (control == "sdown"):
			globales.velocidad = globales.velocidad - 10
			driver.SetSpeed(globales.velocidad)  

		#Control de la cámara
		#Mover a la izquierda
		elif (control == "camleft"):
			servo_l()
		#Mover al centro
		elif (control == "camcenter"):
			servo_c()
		#Mover a la derecha  
		elif (control == "camright"):
			servo_r()	
		#Mover arriba  
		elif (control == "camup"):
			servo_u()	
		#Mover abajao  
		elif (control == "camdown"):
			servo_d()	

	#Variable que guarda la página a cargar
	template = "manual.html"

	#Devuelve el contexto a la página manul
	return render(request, template)

#Funcion que se ejecuta cuando la distancia es menor de la requerida
def BuscarDistanciaMasLarga(sensorDistancia):
	global driver

	#Se para el robot 1 segundo
	driver.Parar()
	time.sleep(1)
	#Funcion asincrona de girar a la izquierda
	Izquierda()
	#Realiza una medida
	distancia1 = sensorDistancia.calcularDistancia()
	#Se para el robot 1 segundo
	driver.Parar()
	time.sleep(1)
	#vuelve a posicion original
	Derecha()
	#Se para el robot 1 segundo
	driver.Parar()
	time.sleep(1)
	#Funcion asincrona de girar a la derecha
	Derecha() 
	#Se para el robot 1 segundo
	driver.Parar()
	time.sleep(1)
	#Realiza otra medida
	distancia2 = sensorDistancia.calcularDistancia()
	#si la distancia de la izquierda es mayor q la derecha,
	#gira dos veces a izq para volver a su posicion
	if distancia1 > distancia2:
		#Actualiza el valor
		globales.distancia=distancia1
		#Funcion asincrona de girar a la izquierda
		Izquierda()
		time.sleep(1)
		#Funcion asincrona de girar a la izquierda
		Izquierda()
		time.sleep(1)
		return
	else:
		globales.distancia=distancia2
		return

#Funcion que controla el modo automatico
def automatico(request):

	global driver

	driver.SetSpeed(35)

	#Variable para salir del bucle while
	salir=0	
	#Se crea el sensor de distancia
	sensorDistancia=SensorDistancia(SFSR02)
	
	#Comienzo de la automatización
	
	while salir == 0:
		#Se obtiene una primera medida de distancia
		globales.distancia = sensorDistancia.calcularDistancia()

		#Comprueba la salida
		if request.session['salir'] == True:
			salir = 1	

		#Si la distancia es menor de 30 busca la distancia mas larga
		if globales.distancia < 30.0:
			BuscarDistanciaMasLarga(sensorDistancia)
		#Si es mayor de 30 prosigue su camino
		else:
			driver.Adelante()

	#Corta el hilo
	salir=0
	request.session['salir'] = False	
	return

#FUncion que llama al control automatico
@login_required(login_url='/')
def auto(request):
	#Indica que está el modo automatico activado
	globales.auto = True

	#Creamos un hilo para ejecutar el automatico así no bloquea a los demas hilos
	globales.automatic = threading.Thread(target=automatico, args=[request])
	globales.automatic.start()

	template = "auto.html"

	return render(request, template)
	
#Funcion que registra a un usuario en el sitema
def registro(request):
		
	#Si el formulario ha sido enviado
	if request.method=='POST':	
		#Se vinculan los datos POST con el formulario UsuarioForm
		form = UsuarioForm(request.POST,request.FILES) 
			
		#Si el formulario pasa todas las reglas de validacion se recogen los datos y se procesan")
		if form.is_valid(): 
			email=form.cleaned_data['email']
			photo = form.cleaned_data.get('photo')
			user=Usuario.objects.filter(email=email)
			#Se comprueba que no exista un usuario con el email introducido
			if(user):
				form._errors['email']="Ya existe un usuario con ese email"
				return render(request, 'registro.html',{'form':form,})
		
			#Antes de guardar el nuevo usuario en la base de datos
			nuevo_usuario=form.save(commit=False)	
			nuevo_usuario.photo = photo
			nuevo_usuario.save()
			username=nuevo_usuario.username
			login='1'
			return redirect(reverse('gracias', kwargs={'username': username , 'login' : login } ))
			
	else:
		#Formulario vacio
		form=UsuarioForm()	
	
	return render(request, 'registro.html',{'form':form})


#Función para loguear al usuario
def login(request):
	#Comprueba autentificación del usuario
	if request.user.is_authenticated():
		return redirect(reverse('index'))
	mensaje = ''
	if request.method == 'POST':
		#Recoge los datos metidos por usuario
		username = request.POST.get('username')
		password = request.POST.get('password')
		#Comprueba los datos
		user = authenticate(username=username, password=password)
		#Si el usuario está logueado pasa a estar activo
		if user is not None:
			if user.is_active:
				auth.login(request, user)
				return redirect(reverse('index'))
			else:
				pass
		mensaje = 'Nombre de usuario o contraseña no valido'
	return render(request, 'login.html', {'mensaje': mensaje})
 
#Función para desloguear usuario
@login_required(login_url='/')
def logout(request):
	auth.logout(request)
	return HttpResponseRedirect('/')

#Función para editar contraseña
@login_required(login_url='/')
def editar_contrasena(request):
	#Se obtiene el usuario
	usuario=request.user    
	if request.method == 'POST':
		#Llama al formulario
		form = EditarContrasenaForm(request.POST)
		#Comprueba formulario
		if form.is_valid():
			#Realiza los cambios
			request.user.password = make_password(form.cleaned_data['password'])
			request.user.save()
			messages.success(request, 'La contraseña ha sido cambiado con exito!.')
			messages.success(request, 'Es necesario introducir los datos para entrar.')
			return render(request, 'editar_contrasena.html', {'form': form, 'usuario': usuario}) 
	else:
		form = EditarContrasenaForm()
	return render(request, 'editar_contrasena.html', {'form': form, 'usuario': usuario})    
 
#editar foto
@login_required(login_url='/')
def editar_foto(request):
	if request.method == 'POST':
		#Crea formulario
		form = EditarFotoForm(request.POST, request.FILES)
		#Comprueba formulario
		if form.is_valid():
			#Realiza cambios
			request.user.photo = form.cleaned_data['imagen']
			request.user.save()
			return render(request, 'editar_foto.html', {'form': form, 'usuario': request.user})
	else:
		form = EditarFotoForm()
	return render(request, 'editar_foto.html', {'form': form, 'usuario': request.user}) 
 
#Función para  dar de baja a un usuario
@login_required(login_url='/')
def eliminar_usuario(request):
	#Se busca usuario
	usuario=request.user
	username = usuario.username
	#Se borra usuario de la base de datos
	usuario.delete()
	login='0'
	return redirect(reverse('gracias', kwargs={'username': username, 'login':login}))
 
#Función para dar las gracias cuando incías, cierras o borras usuario
def gracias(request, username, login):
	return render(request, 'gracias.html', {'username': username, 'login': login})

#Función para sobre mi
def sobre_mi(request):
	return render(request, 'sobre_mi.html')
