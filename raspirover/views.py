#!/usr/bin/env python3.4
# -*- encoding: utf-8 -*- 
from chartit import DataPool, Chart			#para graficas
import django_extensions
from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required   #para loguin
from django.contrib import auth, messages                   #para arreglar error de login() takes exactly 1 argument (2 given)
from django.contrib.auth import authenticate, login, logout #para logout y login                                                    
from django.contrib.auth.hashers import make_password       #para password                                                            
from operator import attrgetter                             #Ordena la lista por un campo del Objeto.
from django.template.loader import get_template
from django.template import Context, RequestContext
from multiprocessing import Process 
from subprocess import call
import asyncio
import time, sys, os
import RPi.GPIO as GPIO
import picamera
import datetime
import threading
import datetime

#Importaciones de ficheros creados para
#sensores, camara, motores y globales.
from .models import *
from .forms import *
from servo import *
from motor import *
from camara import *
from dosMotores import *
from sensorDistancia import *
from sensorLuz import *
from sensorTemperatura import *
from sensorGas import *
from timerRecurrente import *
import globales 


globales.salir = 0
sensorDistancia=SensorDistancia(23,24)

def index(request):

	#Creacion de los motores por parejas
	motorIzq = Motor (27,22,4,100)
	motorDer = Motor (5,6,17,100)

	#Creacion del driver L298N
	globales.driver = DriverDosMotores (motorIzq, motorDer)
	
	return render(request, 'index.html')

#Funcion explorar
@login_required(login_url='/')
def explorar(request):
	
	if request.method == "POST":
		form = ExploracionForm(request.POST)
		if form.is_valid():
			#Se extraen los valores del formulario
			cleaned_data = form.cleaned_data
			globales.stemperatura = cleaned_data.get('temperatura')
			globales.shumedad = cleaned_data.get('humedad')
			globales.sgas =  cleaned_data.get('gas')
			globales.sluz =  cleaned_data.get('luz')
			globales.camara = cleaned_data.get('camara')
			tiempo = cleaned_data.get('tiempo')
			nombre = cleaned_data.get('nombre')
			descripcion = cleaned_data.get('descripcion')
	
			#Se crea una exploracion con parte de los valores del formulario	
			if tiempo is not None:
				dbexplo=Exploracion(nombre=nombre, tiempo=tiempo, usuariofk=request.user, descripcion=descripcion)
				dbexplo.save()			
			#Se ha elegido en el formulario el sensor de temperatura o humedad (es el mismo)			
			if globales.stemperatura == True or globales.shumedad == True:
				#Se crea sensor de Temperatura y humedad (dth22) para manejar con Raspberry
				sensordth = SensorTemperatura(14)

				#Se crea una tabla sensor de temperatura asociado a la exploracion
				if globales.stemperatura == True:
					dbtemperatura = sensorTemperatura(tipo="Temperatura", enable=True)
					dbtemperatura.save()
					dbexplo.sensores.add(dbtemperatura)

				#Se crea una tabla sensor de humedad asociada a la exploracion	
				if globales.shumedad == True:
					dbhumedad = sensorHumedad(tipo="Humedad", enable=True)
					dbhumedad.save()
					dbexplo.sensores.add(dbhumedad)
					dbexplo.save()					

				#Si el tiempo es null se ejecuta el sensor cada segundo			
				if tiempo is None:	
					timerdth = TimerRecurrente(1.0, sensordth.read)
					timerdth.start_timer()
				#Si el tiempo no es null se ejecuta el sensor segun tiempo asignado	
				else:
					timerdth = TimerRecurrente(float(tiempo)-0.2, sensordth.read)
					timerdth.start_timer()
			
			#Se ha elegido en el formulario el sensor de luz		
			if globales.sluz == True:
				#Se crea sensor de Luz para manejar con Raspberry
				sensorluz = SensorLuz(21,20,16)
				#Se crea una tabla sensor de luz asociada a la exploracion	
				dbluz = sensorLuz(tipo="Luz", enable=True)
				dbluz.save()
				dbexplo.sensores.add(dbluz)
				dbexplo.save()
				#Si el tiempo es null se ejecuta el sensor cada segundo			
				if tiempo is None:	
					timerluz = TimerRecurrente(float(tiempo)-0.2, sensorluz.comprobarLuz)
					timerluz.start_timer()
				#Si el tiempo no es null se ejecuta el sensor segun tiempo asignado	
				else:
					timerluz = TimerRecurrente(1.0, sensorluz.comprobarLuz)
					timerluz.start_timer()

			#Se ha elegido en el formulario el sensor de gas
			if globales.sgas == True:
				#Se crea sensor de gas (MQ-2) para manejar con Raspberry
				sensorgas = SensorGas(26)
			#Se crea una tabla sensor de gas asociada a la exploracion	
				dbgas = sensorGas(tipo="Gas", enable=True)
				dbgas.save()
				dbexplo.sensores.add(dbgas)
				dbexplo.save()
				#Si el tiempo es null se ejecuta el sensor cada segundo			
				if tiempo is not None:	
					timergas = TimerRecurrente(float(tiempo)-0.2, sensorgas.comprobarGas)
					timergas.start_timer()
				#Si el tiempo no es null se ejecuta el sensor segun tiempo asignado	
				else:
					timergas = TimerRecurrente(1.0, sensorgas.comprobarGas)
					timergas.start_timer()

			#si se ha elegido cámara para streaming
			if globales.camara == True:
				camara_start()

			#Si no se ha insertado tiempo no hay insercion en base de datos
			if tiempo is not None:
			#se crea un triguer para lanzar la base de datos
				trigger = TimerRecurrente(float(tiempo) , BBDD, args=[dbexplo.id_exploracion])
				trigger.start_timer()

			#Si se ha elegido manual
			if request.method=='POST' and 'manual' in request.POST:				
				return redirect(reverse('manual'))

			#si se ha elegido automatico
			if request.method=='POST' and 'automatico' in request.POST:
				globales.auto=True
				return redirect(reverse('auto'))		
	else:
		form = ExploracionForm()
	context = {'form': form}
	return render(request, 'explorar.html', context)

#funcion para insertar valor de sensores en base de datos
def BBDD(id_exploracion):

	#se busca la exploracion actual
	dbexplo = Exploracion.objects.get(pk=id_exploracion)
	print(dbexplo.nombre)

	#Si está activado el sensor de temperatura
	if globales.stemperatura == True:
		dbtemperatura = sensorTemperatura(temperatura=globales.temperatura, tipo="Temperatura", enable=True)
		dbtemperatura.save()
		dbexplo.sensores.add(dbtemperatura)
		dbexplo.save()

	#Si está activado el sensor de humedad
	if globales.shumedad == True:
		dbhumedad = sensorHumedad(humedad=globales.humedad, tipo="Humedad", enable=True)
		dbhumedad.save()
		dbexplo.sensores.add(dbhumedad)
		dbexplo.save()

	#Si está activado el sensor de gas
	if globales.sgas == True:
		dbgas = sensorGas(gas=globales.gas, tipo="Gas")
		dbgas.save()
		dbexplo.sensores.add(dbgas)
		dbexplo.save()

	#Si está activado el sensor de luz
	if globales.sluz == True:
		dbluz = sensorLuz(luz=globales.luz, tipo="Luz")
		dbluz.save()
		dbexplo.sensores.add(dbluz)
		dbexplo.save()


#funcion Analizar
@login_required(login_url='/')
def analizar(request):
	#extraer todas las exploraciones del usuario
	explo=Exploracion.objects.filter(usuariofk=request.user)
	return render(request, 'analizar.html', {'explo': explo})

#Funcion que muestra detalles de una exploracion
def detallesExploracion (request, id_exploracion):
	#variables para la página
	t = "Temperatura"
	h = "Humedad"
	l = "Luz"
	g = "Gas"
	temperatura=False
	humedad=False
	gas=False
	luz=False

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
	
	context = {'explo':explo, 't':t, 'h':h, 'l':l, 'g':g, 'temperatura':temperatura, 'humedad':humedad, 'gas':gas, 'luz':luz}
	return render(request, 'detalleExploracion.html', context)

#Funcion que muestra detalles de una exploracion
@login_required(login_url='/')
def mostrarGrafica (request, id_exploracion, sensor_tipo):
	#extraer el sensor seleccionado
	
	explo = Exploracion.objects.get(pk=id_exploracion)

	if sensor_tipo == "Temperatura":
		titulo = "Gráfica de la exploracion " + explo.nombre + " de Temperatura" 
		sensor =  sensorTemperatura.objects.filter(exploracion=explo )

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
		context = {'sensor':sensor, 'chart': cht, 'tipo': sensor_tipo ,'explo' : explo}

		return render(request, 'mostrarGrafica.html', context)

	#Se ha elegido mostrar humedad
	if sensor_tipo == "Humedad":
		titulo = "Grafica de la exploracion " + explo.nombre + " de Humedad" 
		sensor =  sensorHumedad.objects.filter(exploracion=explo )

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
		context = {'sensor':sensor, 'chart': cht, 'tipo': sensor_tipo ,'explo' : explo}

		return render(request, 'mostrarGrafica.html', context)

	#Se ha elegido mostrar gas
	if sensor_tipo == "Gas":
		titulo = "Grafica de la exploracion " + explo.nombre + " de Gas" 
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
		context = {'sensor':sensor, 'chart': cht, 'tipo': sensor_tipo ,'explo' : explo}

		return render(request, 'mostrarGrafica.html', context)

	#Se ha elegido mostrar luz
	if sensor_tipo == "Luz":
		titulo = "Grafica de la exploracion " + explo.nombre + " de Luz" 
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
		context = {'sensor':sensor, 'chart': cht, 'tipo': sensor_tipo ,'explo' : explo}

		return render(request, 'mostrarGrafica.html', context)

#funcion para salir del modo de control
@login_required(login_url='/')
def salir(request):

	#Destruye los timers
	globales.salir=1
	#Inicializa los GPIO
	GPIO.cleanup()

	#Para la cámara
	camara_stop()

	#si estaba en automático
	if globales.auto == True:
		#borra hilo de automático
		del globales.automatic
		#reinicia la variable
		globales.auto = False

	#reinicia todas las variables	
	globales.inicializar()

	return redirect(reverse('index'))

#Función que muestra los datos de los sensores
#En la pantalla de control del sistema
@login_required(login_url='/')
def mostrardatos(request):
	context = {'temperatura': globales.temperatura, 'humedad': globales.humedad, 'gas' : globales.gas, 'luz' : globales.luz, 
	'stemp' : globales.stemperatura, 'shum' : globales.shumedad, 'sgas' : globales.sgas, 'sluz' : globales.sluz, 'camara':globales.camara }

	template = "datos.html"
	return render(request, template, context)

#Funcion para girar a la derecha
def Derecha():
	eventloop = asyncio.new_event_loop()
	asyncio.set_event_loop(eventloop)
	eventloop.run_until_complete(globales.driver.GirarDerAsync()) 
	eventloop.close()

#Funcion para girar a la izquierda
def Izquierda():
	eventloop = asyncio.new_event_loop()
	asyncio.set_event_loop(eventloop)
	eventloop.run_until_complete(globales.driver.GirarIzqAsync()) 
	eventloop.close()

#Funcion que se ejecuta cuando la distancia es menor de la requerida
def BuscarDistanciaMasLarga():
	driver=globales.driver
	global sensorDistancia
	
	driver.Parar()
	time.sleep(1)
	#girar a la izquiera y toma medida
	Izquierda()
	distancia1 = float(sensorDistancia.precisionDistancia())
	driver.Parar()
	time.sleep(1)
	#vuelve a posicion original
	Derecha()
	driver.Parar()
	time.sleep(1)
	#gira a la derecha y toma medida
	Derecha()
	driver.Parar()
	time.sleep(1)
	distancia2 = float(sensorDistancia.precisionDistancia())
	time.sleep(1)
	#si la distancia de la izq es mayor q la derecha gira dos veces a izq para volver a su posicion
	if distancia1 > distancia2:
		Izquierda()
		time.sleep(1)	
		Izquierda()
		time.sleep(1)
		driver.Parar()

#funcion Manual
@login_required(login_url='/')
def manual(request):

	#Control manual del robot
	#Se recoge la peticion de movimiento
	if 'cmd' in request.GET and request.GET['cmd']:
		control = request.GET['cmd']

		#Control del robot
		#Mover hacia adelante
		if (control == "fwd"):
			globales.driver.Adelante()
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

	#Se crea un contexto con las variables para devolver a la plantilla
	context = {'temperatura': globales.temperatura, 'humedad': globales.humedad, 
			'gas' : globales.gas, 'luz' : globales.luz, 'stemp' : globales.stemperatura, 
			'shum' : globales.shumedad, 'sgas' : globales.sgas, 'sluz' : globales.sluz, 
			'camara':globales.camara }

	#Variable que guarda la página a cargar
	template = "manual.html"

	#Devuelve el contexto a la página manul
	return render_to_response(template, context, context_instance=RequestContext(request))



def automatico():
	global sensorDistancia	
	print("entro en modo auto")
	print("He creado el sensor y entro a bucle")
	#Comienzo de la automatización
	while True:
		print("estoy en bucle")
		globales.distancia = float(sensorDistancia.precisionDistancia() - 20 )	
		print ("Distancia: %.2f" % globales.distancia)
		if globales.distancia < 30.0:
			BuscarDistanciaMasLarga()
		else:
			globales.driver.Adelante()


@login_required(login_url='/')
def auto(request):

	context = {'temperatura': globales.temperatura, 'humedad': globales.humedad, 'gas' : globales.gas, 'luz' : globales.luz, 
	'stemp' : globales.stemperatura, 'shum' : globales.shumedad, 'sgas' : globales.sgas, 'sluz' : globales.sluz, 'camara':globales.camara }

	globales.automatic=threading.Thread(target=automatico)
	globales.automatic.start()
	print("creo hilo")					
	template = "auto.html"
	return render(request, template, context)
	
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
				return render_to_response('registro.html',{'form':form}, context_instance=RequestContext(request))
		
			#Antes de guardar el nuevo usuario en la base de datos
			nuevo_usuario=form.save(commit=False)	
			nuevo_usuario.photo = photo
			nuevo_usuario.save()
			username=nuevo_usuario.username
			login='1'
			return redirect(reverse('gracias', kwargs={'username': username , 'login' : login } ))
			
			#Cuando se registra un usuario nuevo se logea automaticamente
			#acceso=authenticate(username=nuevo_usuario.username,password=form.cleaned_data['password'])
			#if acceso is not None:	# Usuario válido
			#	if acceso.is_active:
			#		login(request,acceso)
			#		return HttpResponseRedirect('index/')
			#
			#return HttpResponseRedirect('/')
	else:
		form=UsuarioForm()	#Formulario vacio
	return render_to_response('registro.html',{'form':form}, context_instance=RequestContext(request))


# para loguear al usuario
def login(request):
	if request.user.is_authenticated():
		return redirect(reverse('index'))
	mensaje = ''
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				auth.login(request, user)
				return redirect(reverse('index'))
			else:
				pass
		mensaje = 'Nombre de usuario o contraseña no valido'
	return render(request, 'login.html', {'mensaje': mensaje})
 
#desloguear usuario
@login_required(login_url='/')
def logout(request):
#	logout(request)
	auth.logout(request)
	return HttpResponseRedirect('/')

#editar contraseña
@login_required(login_url='/')
def editar_contrasena(request):
	usuario=request.user    
	if request.method == 'POST':
		form = EditarContrasenaForm(request.POST)
		if form.is_valid():
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
		form = EditarFotoForm(request.POST, request.FILES)
		if form.is_valid():
			request.user.photo = form.cleaned_data['imagen']
			request.user.save()
			return render(request, 'editar_foto.html', {'form': form, 'usuario': request.user})
	else:
		form = EditarFotoForm()
	return render(request, 'editar_foto.html', {'form': form, 'usuario': request.user}) 
 
#dar de baja a un usuario
@login_required(login_url='/')
def eliminar_usuario(request):
	usuario=request.user
	usuario.delete()
	login='0'
	return redirect(reverse('gracias', kwargs={'username': username, 'login':login}))
 

def gracias(request, username, login):
	return render(request, 'gracias.html', {'username': username, 'login': login})

#sobre mi
def sobre_mi(request):
	return render(request, 'sobre_mi.html')

