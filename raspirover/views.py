#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

########################## LIBRERÍAS ###############################

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
#Librería para controlar GPIO
import RPi.GPIO as GPIO
#Librería para usar PiCamera
import picamera
#Libreria para hilos
import threading
#Libreria para Max, min y avg
from django.db.models import Avg, Max, Min

#Libreria del sistema operativo
#os.nice(49)

#Importaciones de ficheros creados para
#sensores, camara, motores y globales.
from .models import *
from .forms import *
from servo import *
from motor import *
from camara import *
from dosMotores import *
from sensores import *
from globales import * 
from voltaje import *
from timer import *
from sensors import *
#from gpiozero import *

########################## MANAGER DE TAREAS ##########################

s = Scheduler()

########################## VOLTAJE ##########################

spi = SPI(canalBateria=1, canalGas = 2, canalLuz = 3)

voltaje = Task(30.0, spi.ObtenerBateria)

voltaje.start_timer()

########################## CONTROLADOR ###############################

#Creacion de los motores por parejas
motorIzq = Motor (27,22)
motorDer = Motor (5,6)

#Creacion del driver L298N
globales.driver = DriverDosMotores (motorIzq, motorDer)	

########################## INICIO  ###############################

#funcion para apagar el sistema
def apagar(request):
	os.system("sudo shutdown -h now")	

#funcion para reiniciar el sistema
def reboot(request):
	os.system("sudo reboot")	

#Función de la página principal del programa
def index(request):
	#reinicia todas las variables
	globales.salir=1
	globales.auto=False
	globales.manu=False
#	salir(request)
	globales.inicializar()
	globales.salir=0
	
	#Centra la camara
	servo_c()

	#Se inicializa los puertos GPIO
	setup(14,21,20,16,26,22,27,5,6,12)

	#devuelve los valores a la pagina
	context = {'voltaje': globales.porcentaje}
	return render(request, 'index.html', context)

#Funcion que ofrece las opciones para iniciar una exploración
@login_required(login_url='/')
def explorar(request):
	#Si es método post
	if request.method == "POST":
		#se crea un formulaio
		form = ExploracionForm(request.POST)
		#Si el formulario es válido
		if form.is_valid():
			#Se extraen los valores del formulario
			cleaned_data = form.cleaned_data
			globales.stemperatura = cleaned_data.get('temperatura')
			globales.shumedad = cleaned_data.get('humedad')
			globales.sgas =  cleaned_data.get('gas')
			globales.sluz =  cleaned_data.get('luz')
			globales.camara = cleaned_data.get('camara')
			globales.tiempo = cleaned_data.get('tiempo')
			nombre = cleaned_data.get('nombre')
			descripcion = cleaned_data.get('descripcion')
	
			#Se crea una exploracion con parte de los valores del formulario
			#Si tiempo no está vacío se crea una exploracion	
			if globales.tiempo is not None:
				globales.dbexplo=Exploracion(nombre=nombre, tiempo=globales.tiempo, usuariofk=request.user, descripcion=descripcion)
				globales.dbexplo.save()
				#Si la camara está activada
				if globales.camara == True:
					dbcamara = sensorCamara(video=nombre+str(globales.dbexplo.id_exploracion)+".mp4", tipo="Camara", enable=True)
					dbcamara.save()
					globales.dbexplo.sensores.add(dbcamara)
					globales.dbexplo.save()
					camara_start()

			#Se ha elegido en el formulario el sensor de temperatura o humedad (es el mismo)			
			if globales.stemperatura == True or globales.shumedad == True:
				#Se crea una tabla sensor de temperatura asociado a la exploracion
				if globales.stemperatura == True and globales.tiempo is not None:
					dbtemperatura = sensorTemperatura(tipo="Temperatura", enable=True)
					dbtemperatura.save()
					globales.dbexplo.sensores.add(dbtemperatura)
					globales.dbexplo.save()

				#Se crea una tabla sensor de humedad asociada a la exploracion	
				if globales.shumedad == True and globales.tiempo is not None:
					dbhumedad = sensorHumedad(tipo="Humedad", enable=True)
					dbhumedad.save()
					globales.dbexplo.sensores.add(dbhumedad)
					globales.dbexplo.save()

				#Si el tiempo es null se ejecuta el sensor cada 1 segundo			
				if globales.tiempo is None:	
					#timerdth = TimerRecurrente(1.00, comprobarth)
					#timerdth.start_timer()
					s.AddTask( 1.00, comprobarth )

				#Si el tiempo no es null se crea un timer de x segundos definidos por la variable tiempo
				else:
					#timerdth = TimerRecurrente(globales.tiempo, comprobarth)
					#timerdth.start_timer()
					s.AddTask( globales.tiempo, comprobarth )

			#Se ha elegido en el formulario el sensor de luz		
			if globales.sluz == True:
				#Se crea sensor de Luz para manejar con Raspberry
				#sensorluz = SensorLuz(21,20,16)
				#Se crea un timer de x segundos definidos por la variable tiempo
				if globales.tiempo is not None:	
					#Se crea una tabla sensor de luz asociada a la exploracion	
					dbluz = sensorLuz(tipo="Luz", enable=True)
					dbluz.save()
					globales.dbexplo.sensores.add(dbluz)
					globales.dbexplo.save()
					#Se crea un timer de x segundos definidos por la variable tiempo
					#timerluz = TimerRecurrente(globales.tiempo,  sensorluz.comprobarLuz)
					#timerluz.start_timer()
					s.AddTask( globales.tiempo, spi.ObtenerLuz)

				#Si el tiempo es null se ejecuta el sensor cada 5 segundos	
				else:
					#Se crea un timer de 1 segundo
					#timerluz = TimerRecurrente(1.00, sensorluz.comprobarLuz)
					#timerluz.start_timer()
					s.AddTask( 1.00 , spi.ObtenerLuz)

			#Se ha elegido en el formulario el sensor de gas
			if globales.sgas == True:
				#Se crea sensor de gas (MQ-2) para manejar con Raspberry
				#sensorgas = SensorGas(26)
				#Si el tiempo no es null se ejecuta el sensor segun tiempo asignado	
				if globales.tiempo is not None:
					#Se crea una tabla sensor de gas asociada a la exploracion	
					dbgas = sensorGas(tipo="Gas", enable=True)
					dbgas.save()
					globales.dbexplo.sensores.add(dbgas)
					globales.dbexplo.save()

				#Se crea un timer de x segundos definidos por la variable tiempo
					#timergas = TimerRecurrente(globales.tiempo, sensorgas.comprobarGas)
					#timergas.start_timer()
					s.AddTask( globales.tiempo , spi.ObtenerGas)

				#Si el tiempo es null se ejecuta el sensor cada 5 segundos			
				else:
					#Se crea un timer de 1 segundo
					#timergas = TimerRecurrente(1.00, sensorgas.comprobarGas)
					#timergas.start_timer()
					s.AddTask( 1.00 , spi.ObtenerGas)

			#Si se ha elegido cámara para streaming
			if globales.camara == True:
				camara_start()
			
			#Si se ha insertado tiempo se lanza un trigger para la bbdd
			#definida por la variable tiempo
			if globales.tiempo is not None:
				#trigger = TimerRecurrente(globales.tiempo , BBDD, args=[globales.dbexplo.id_exploracion])
				#trigger.start_timer()
				s.AddTask( globales.tiempo, BBDD, args=[globales.dbexplo.id_exploracion] )

			#Si se ha elegido manual
			if request.method=='POST' and 'manual' in request.POST:				
				#Activa todos los sensores asignados
				#global s
				s.StartAllTasks()
				return redirect(reverse('manual'))

			#si se ha elegido automatico
			if request.method=='POST' and 'automatico' in request.POST:
				return redirect(reverse('auto'))

	else:
		form = ExploracionForm()
	context = {'form': form, 'voltaje': globales.porcentaje}
	return render(request, 'explorar.html', context)

#Funcion que guarda valores de sensores en la base de datos
@transaction.atomic
def BBDD(id_exploracion):

#	inicio = time.monotonic()
	#Se busca la exploracion actual
	globales.dbexplo = Exploracion.objects.get(pk=id_exploracion)

	#Si está activado el sensor de temperatura
	if globales.stemperatura == True:
		#Se añade un nuevo valor de temperatura a la base de datos
		dbtemperatura = sensorTemperatura(temperatura=globales.temperatura, tipo="Temperatura", enable=True)
		dbtemperatura.save()
		globales.dbexplo.sensores.add(dbtemperatura)

		#Si está activado el sensor de humedad
	if globales.shumedad == True:
		#Se añade un nuevo valor de humedad a la base de datos
		dbhumedad = sensorHumedad(humedad=globales.humedad, tipo="Humedad", enable=True)
		dbhumedad.save()
		globales.dbexplo.sensores.add(dbhumedad)

		#Si está activado el sensor de gas
	if globales.sgas == True:
		#Se añade un nuevo valor de gas a la base de datos
		dbgas = sensorGas(gas=globales.gas, tipo="Gas")
		dbgas.save()
		globales.dbexplo.sensores.add(dbgas)

	#Si está activado el sensor de luz
	if globales.sluz == True:
		#Se añade un nuevo valor de luz a la base de datos
		dbluz = sensorLuz(luz=globales.luz, tipo="Luz")
		dbluz.save()
		globales.dbexplo.sensores.add(dbluz)

	#	print(time.monotonic() - inicio)	

#Funcion que accede a la página Analizar
@login_required(login_url='/')
def analizar(request):
	globales.salir=1
	#salir(request)
	globales.inicializar()
	#extraer todas las exploraciones del usuario
	explo=Exploracion.objects.filter(usuariofk=request.user)

	return render(request, 'analizar.html', {'explo': explo, 'voltaje': globales.porcentaje})

#Elimina una exploración elegida por el usuario
@login_required(login_url='/')
def eliminarExploracion(request, id_exploracion):
	#Busca la exploracion
	explo = Exploracion.objects.get(pk=id_exploracion)
	#elimina el video
	os.system("sudo rm -rf /home/pi/proyecto/media/videos/"+explo.nombre+str(explo.id_exploracion)+".mp4")
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
	c = "Camara"
	temperatura=False
	humedad=False
	gas=False
	luz=False
	camara=False

	#extraer solo la exploracion seleccionada
	explo = Exploracion.objects.get(pk=id_exploracion)
	#extraer los sensores utilizados en la exploracion
	sensores = Sensor.objects.filter(exploracion=explo)
	#recorrer los sensores para saber cuales estan detectados
	#y pasarlos a la pagina
	for x in sensores:
		if x.tipo == "Temperatura":
			temperatura=True
		if x.tipo == "Humedad":
			humedad=True
		if x.tipo == "Gas":
			gas=True
		if x.tipo == "Luz":
			luz=True
		if x.tipo == "Camara":
			video = sensorCamara.objects.filter(exploracion=explo)
			camara=True
	
	context = {'explo':explo, 'c':c, 't':t, 'h':h, 'l':l, 'g':g, 'camara':camara, 'voltaje': globales.porcentaje, 'temperatura':temperatura, 'humedad':humedad, 'gas':gas, 'luz':luz, 'video':video}
	return render(request, 'detalleExploracion.html', context)

#Funcion que muestra una gráfica seleccionada
@login_required(login_url='/')
def mostrarGrafica (request, id_exploracion, sensor_tipo):
	#con sensor_tipo se sabe la gráfica que se ha seleccionado
	explo = Exploracion.objects.get(pk=id_exploracion)

	#Se ha seleccionado gráfica de temperatura
	if sensor_tipo == "Temperatura":
		titulo = "Gráfica de la exploracion " + explo.nombre + " de Temperatura" 
		sensor =  sensorTemperatura.objects.filter(exploracion=explo )

		min = sensor.aggregate(Min('temperatura')).get('temperatura__min', 0.00)
		max = sensor.aggregate(Max('temperatura')).get('temperatura__max', 0.00)
		avg = round(sensor.aggregate(Avg('temperatura')).get('temperatura__avg', 0.00),2)

		#paso 1: Crear el datapool con los datos que queremos recibir.
		data = \
			DataPool(
			   series=
				[{'options': {
				   'source': sensorTemperatura.objects.filter(exploracion=explo)},
				  'terms': [
					('fecha',lambda d: d.strftime("%H:%M:%S") ),
					'temperatura']}
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
						'temperatura']
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
		context = {'voltaje': globales.porcentaje, 'sensor':sensor, 'chart': cht, 'tipo': sensor_tipo ,'explo' : explo, 'min' : min , 'max' : max , 'avg' : avg }

		return render(request, 'mostrarGrafica.html', context)

	#Se ha seleccionado gráfica de humedad
	elif sensor_tipo == "Humedad":
		titulo = "Gráfica de la exploracion " + explo.nombre + " de Humedad" 
		sensor =  sensorHumedad.objects.filter(exploracion=explo )

		min = sensor.aggregate(Min('humedad')).get('humedad__min', 0.00)
		max = sensor.aggregate(Max('humedad')).get('humedad__max', 0.00)
		avg = round(sensor.aggregate(Avg('humedad')).get('humedad__avg', 0.00),2)

		#paso 1: Crear el datapool con los datos que queremos recibir.
		data = \
			DataPool(
			   series=
				[{'options': {
				   'source': sensorHumedad.objects.filter(exploracion=explo)},
				  'terms': [
					('fecha',lambda d: d.strftime("%H:%M:%S") ),
					'humedad']}
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
						'humedad']
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
		context = {'voltaje': globales.porcentaje, 'sensor':sensor, 'chart': cht, 'tipo': sensor_tipo ,'explo' : explo, 'min' : min , 'max' : max , 'avg' : avg }

		return render(request, 'mostrarGrafica.html', context)

	#Se ha seleccionado gráfica de Gas
	elif sensor_tipo == "Gas":
		titulo = "Gráfica de la exploracion " + explo.nombre + " de Gas" 
		sensor =  sensorGas.objects.filter(exploracion=explo)

		#paso 1: Crear el datapool con los datos que queremos recibir.
		data = \
			DataPool(
			   series=
				[{'options': {
				   'source': sensorGas.objects.filter(exploracion=explo)},
				  'terms': [
					('fecha',lambda d: d.strftime("%H:%M:%S") ),
					'gas']}
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
						'gas']
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
		context = {'voltaje': globales.porcentaje, 'sensor':sensor, 'chart': cht, 'tipo': sensor_tipo ,'explo' : explo}

		return render(request, 'mostrarGrafica.html', context)

	#Se ha seleccionado gráfica de Luz
	elif sensor_tipo == "Luz":
		titulo = "Gráfica de la exploracion " + explo.nombre + " de Luz" 
		sensor =  sensorLuz.objects.filter(exploracion=explo)

		#paso 1: Crear el datapool con los datos que queremos recibir.
		data = \
			DataPool(
			   series=
				[{'options': {
				   'source': sensorLuz.objects.filter(exploracion=explo)},
				  'terms': [
					('fecha',lambda d: d.strftime("%H:%M:%S") ),
					'luz']}
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
						'luz']
					  }}],
				chart_options={
					'title': {
						'text': titulo},
					'xAxis': {
						'title': {
							'text': 'Tiempo'}},
					'yAxis': {
						'title': {
							'text': 'Luz'}},
					'legend': {
						'enabled': False},
					'credits': {
						'enabled': False}})
								
		#paso 3: Enviar la gráfica a la página.
		context = {'sensor':sensor, 'chart': cht, 'tipo': sensor_tipo ,'explo' : explo, 'voltaje': globales.porcentaje}

		return render(request, 'mostrarGrafica.html', context)

#Funcion para salir del modo de control
@login_required(login_url='/')
def salir(request):

	global s

	#Para el Manager del sistema
	s.StopAllTasks()
#	del globales.manager

	#Centra la camara
	servo_c()

	#Destruye los timers
	globales.salir=1
	
	#Para la cámara
	if globales.camara == True:
	#	if globales.tiempo is not None:
	#		globales.nombreFichero=globales.dbexplo.nombre + str(globales.dbexplo.id_exploracion)			
	#		camara_stop(globales.nombreFichero)
		camara_parar()

	#si estaba en automático
	if globales.auto == True:
		#borra hilo de automático
		globales.auto=False
		del globales.automatic

	#si estaba en manual
	if globales.manu == True:
		#borra hilo de automático
		globales.manu=False
		del globales.manual

	#redirige al index
	return redirect('index')

#Función que muestra los datos de los sensores en pantalla modo de control
#En la pantalla de control del sistema
@login_required(login_url='/')
def mostrardatos(request):

	context = {'temperatura': globales.temperatura, 'humedad': globales.humedad, 'gas' : globales.gas, 'luz' : globales.luz,
	'stemp' : globales.stemperatura, 'shum' : globales.shumedad, 'sgas' : globales.sgas, 'sluz' : globales.sluz, 'camara':globales.camara, 'voltaje': globales.porcentaje, 'numVideos': globales.grabacion}

	template = "datos.html"
	return render(request, template, context)

#Funcion para girar a la derecha en asincrono
def Derecha():
	eventloop = asyncio.new_event_loop()
	asyncio.set_event_loop(eventloop)
	eventloop.run_until_complete(globales.driver.GirarDerAsync()) 
	eventloop.close()

#Funcion para girar a la izquierda en asincrono
def Izquierda():
	eventloop = asyncio.new_event_loop()
	asyncio.set_event_loop(eventloop)
	eventloop.run_until_complete(globales.driver.GirarIzqAsync()) 
	eventloop.close()

def manu(request):

	#Se recoge la peticion de wmovimiento
	if 'cmd' in request.GET and request.GET['cmd']:
		control = request.GET['cmd']

		#Control del robot
		#Mover hacia adelante
		if (control == "fwd"):
			eventloop = asyncio.new_event_loop()
			asyncio.set_event_loop(eventloop)
			eventloop.run_until_complete(globales.driver.Adelante())
			eventloop.close()
			#globales.driver.Adelante()
		#Mover hacia atras
		if (control == "bwd"):
			globales.driver.Atras()
		#Mover a la izquierda
		if (control == "left"):
			globales.driver.Izquierda()
		#Mover a la derecha
		if (control == "right"):
			globales.driver.Derecha()
		#Parar los motors		
		if (control == "stop"):
			globales.driver.Parar()  	

		#Control de la cámara
		#Mover a la izquierda
		if (control == "camleft"):
			servo_l()
		#Mover al centro
		if (control == "camcenter"):
			servo_c()
		#Mover a la derecha  
		if (control == "camright"):
			servo_r()	
		#Mover arriba  
		if (control == "camup"):
			servo_u()	
		#Mover abajao  
		if (control == "camdown"):
			servo_d()	

#Función de control manual del sistema
@login_required(login_url='/')
def manual(request):

	#Activar modo manual	
	globales.manu=True

#	globales.manager=threading.Thread(target=s.StartAllTasks())
#	globales.manager.start()


	#Crear hilo de modo manual
	globales.manual=threading.Thread(target=manu(request)).setDaemon(True)
	#globales.manual.start()

	#Se crea un contexto con las variables para devolver a la plantilla
	context = {'temperatura': globales.temperatura, 'humedad': globales.humedad, 
			'gas' : globales.gas, 'luz' : globales.luz, 'stemp' : globales.stemperatura, 
			'shum' : globales.shumedad, 'sgas' : globales.sgas, 'sluz' : globales.sluz, 
			'camara':globales.camara, 'voltaje': globales.porcentaje}

	#Variable que guarda la página a cargar
	template = "manual.html"

	#Devuelve el contexto a la página manul
	return render(request, template, context)
	#return render_to_response(template, context, context_instance=RequestContext(request))

#Funcion que se ejecuta cuando la distancia es menor de la requerida
def BuscarDistanciaMasLarga(sensorDistancia):
	driver=globales.driver
	
	#Se para el robot 1 segundo
	driver.Parar()
	time.sleep(1)
	#Funcion asincrona de girar a la izquierda
	Izquierda()
	#Realiza una medida
	distancia1 = sensorDistancia.precisionDistancia()
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
	distancia2 = sensorDistancia.precisionDistancia()
	
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
def automatico():
	salir=0	#Variable para salir del bucle while
	#Se crea el sensor de distancia
	sensorDistancia=SensorDistancia(23,24)
	
	#Comienzo de la automatización
	
	#Se toma una primera medida
	globales.distancia = float(sensorDistancia.precisionDistancia())

	while salir == 0:
		#Se obtiene una primera medida de distancia
		globales.distancia = float(sensorDistancia.precisionDistancia())
		#Si la distancia es menor de 30 busca la distancia mas larga
		if globales.distancia < 30.0:
			BuscarDistanciaMasLarga(sensorDistancia)
		#Si es mayor de 30 prosigue su camino
		else:
			globales.driver.Adelante()
		#Comprueba la salida
		if globales.salir == 1:
			salir = 1
			globales.auto = False		

	#Corta el hilo
	salir=0
	globales.salir=0	
	return

#FUncion que llama al control automatico
@login_required(login_url='/')
def auto(request):
	#Indica que está el modo automatico activado
	globales.auto=True	

	#Activa todos los sensores asignados
#	s.StartAllTasks()

	#Creamos un hilo para ejecutar el automatico
	#así no bloquea a los demas hilos
	globales.automatic=threading.Thread(target=automatico)
	globales.automatic.start()

	#creamos el contexto
	context = {'temperatura': globales.temperatura, 'humedad': globales.humedad, 'gas' : globales.gas, 'luz' : globales.luz, 
	'stemp' : globales.stemperatura, 'shum' : globales.shumedad, 'sgas' : globales.sgas, 'sluz' : globales.sluz, 'camara':globales.camara, 'voltaje': globales.porcentaje }
	
	template = "auto.html"
	return render(request, template, context)
	#return render_to_response(template, context, context_instance=RequestContext(request))
	
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
				return render(request, 'registro.html',{'form':form, 'voltaje': globales.porcentaje})
		
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
	
	return render(request, 'registro.html',{'form':form, 'voltaje': globales.porcentaje})


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
	return render(request, 'login.html', {'mensaje': mensaje, 'voltaje': globales.porcentaje})
 
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
	return render(request, 'editar_contrasena.html', {'form': form, 'voltaje': globales.porcentaje, 'usuario': usuario})    
 
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
	return render(request, 'editar_foto.html', {'form': form, 'voltaje': globales.porcentaje, 'usuario': request.user}) 
 
#Función para  dar de baja a un usuario
@login_required(login_url='/')
def eliminar_usuario(request):
	#Se busca usuario
	usuario=request.user
	username = usuario.username
	#Se borra usuario de la base de datos
	usuario.delete()
	login='0'
	return redirect(reverse('gracias', kwargs={'username': username, 'login':login, 'voltaje': globales.porcentaje}))
 
#Función para dar las gracias cuando incías, cierras o borras usuario
def gracias(request, username, login):
	return render(request, 'gracias.html', {'username': username, 'login': login, 'voltaje': globales.porcentaje})

#Función para sobre mi
def sobre_mi(request):
	
	return render(request, 'sobre_mi.html', {'voltaje': globales.porcentaje})

