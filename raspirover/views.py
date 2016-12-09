#!/usr/bin/env python3.4
# -*- encoding: utf-8 -*- 
from graphos.sources.simple import SimpleDataSource
from graphos.renderers.gchart import LineChart
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

				#Se crea una tabla sensor de temperatura asociada a la exploracion
				if globales.stemperatura == True:
					dbtemperatura = sensorTemperatura(tipo="Temperatura", enable=True )
					dbtemperatura.save()
					dbexplo.sensores.add(dbtemperatura)
				#Se crea una tabla sensor de humedad asociada a la exploracion	
				if globales.shumedad == True:
					dbhumedad = sensorHumedad(tipo="Humedad", enable=True)
					dbhumedad.save()
					dbexplo.sensores.add(dbhumedad)

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
				trigger = TimerRecurrente(float(tiempo) , BBDD, args=(dbexplo.id_exploracion,dbtemperatura.id_sensor))
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
def BBDD(id_exploracion, id_sensortemp):

	dbexplo = Exploracion.objects.get(pk=id_exploracion)
	print(dbexplo.nombre)

	if globales.stemperatura == True:
		print("almaceno temperatura")
		#se crea un nuevo registro de temperatura
		dbtemperatura = temperatura(temperatura=globales.temperatura)
		#se agrega a la base de datos
		dbtemperatura.save()
		dbexplo.sensores.temperatura.temperaturafk.add(dbgas)
	
		
				
	if globales.shumedad == True:
		print("almaceno temperatura")
		#se crea un nuevo registro de temperatura
		dbhumedad = humedad(humedad=globales.humedad)
		#se agrega a la base de datos
		dbhumedad.save()
		sh = dbexplo.sensores.get(tipo="Humedad")
		print(sh)
		print(sh.tipo)	
		sh.humedadfk=dbhumedad
		sh.save()

	if globales.sgas == True:
		dbgas = gas(gas=globales.gas)
		dbgas.save()
		dbexplo.sensores.gas.add(dbgas)

	if globales.sluz == True:
		dbluz = luminosidad(luz=globales.luz)
		dbluz.save()
		dbexplo.sensores.luminosidad.add(dbluz)


#funcion Analizar
@login_required(login_url='/')
def analizar(request):
	#extraer todas las exploraciones del usuario
	explo=Exploracion.objects.filter(usuariofk=request.user)
	return render(request, 'analizar.html', {'explo': explo})

#Funcion que muestra detalles de una exploracion
def detallesExploracion (request, id_exploracion):
	#extraer solo la exploracion seleccionada
	explo = Exploracion.objects.get(pk=id_exploracion)
	context = {'explo':explo}
	return render(request, 'detalleExploracion.html', context)

#Funcion que muestra detalles de una exploracion
def mostrarGrafica (request, id_sensor):
	#extraer el sensor seleccionado
	
	sensor = Sensor.objects.get(pk=id_sensor)
	print(sensor.temperaturafk)

	print(sensor.tipo)

	if sensor.tipo == 'Temperatura':
		queryset = sensorTemperatura.objects.get(pk=id_sensor)

	print(queryset.id_sensor)
	print(queryset.enable)
	print(queryset.fecha)
	print(queryset.temperaturafk)

	#queryset = sensor.temperaturafk.all()
	#print(queryset)

	#data_source = ModelDataSource(queryset,fields=['temperaturafk', 'fecha'])
	#chart = LineChart(SimpleDataSource(data=data_source))
	#context = {'sensor':sensor, 'chart': chart}
	context = {'sensor':sensor}
	return render(request, 'mostrarGrafica.html', context)


#funcion para salir del modo de control
@login_required(login_url='/')
def salir(request):

	GPIO.cleanup()

	#se para la cámara
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

	t = get_template('manual.html')
	#Control manual del robot
	if 'cmd' in request.GET and request.GET['cmd']:
		control = request.GET['cmd']

		#Control del robot
		if (control == "fwd"):
			globales.driver.Adelante()
		if (control == "bwd"):
			globales.driver.Atras()
		if (control == "left"):
			globales.driver.Izquierda()
		if (control == "right"):
			globales.driver.Derecha()		
		if (control == "stop"):
			globales.driver.Parar()  	

		#Control de la cámara
		if (control == "camleft"):
			servo_l()
		if (control == "camcenter"):
			servo_c()  
		if (control == "camright"):
			servo_r()	


	context = {'temperatura': globales.temperatura, 'humedad': globales.humedad, 'gas' : globales.gas, 'luz' : globales.luz, 
	'stemp' : globales.stemperatura, 'shum' : globales.shumedad, 'sgas' : globales.sgas, 'sluz' : globales.sluz, 'camara':globales.camara }

	template = "manual.html"
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
	q=UserProfile.objects.get(user=request.user)    
	if request.method == 'POST':
		form = EditarContrasenaForm(request.POST)
		if form.is_valid():
			request.user.password = make_password(form.cleaned_data['password'])
			request.user.save()
			messages.success(request, 'La contraseña ha sido cambiado con exito!.')
			messages.success(request, 'Es necesario introducir los datos para entrar.')
			return render(request, 'editar_contrasena.html', {'form': form, 'seguido': q}) 
	else:
		form = EditarContrasenaForm()
	return render(request, 'editar_contrasena.html', {'form': form, 'seguido': q})    
 
#editar foto
@login_required(login_url='/')
def editar_foto(request):
	if request.method == 'POST':
		form = EditarFotoForm(request.POST, request.FILES)
		if form.is_valid():
			request.user.user_profile.photo = form.cleaned_data['imagen']
			request.user.user_profile.save()
			return render(request, 'editar_foto.html', {'form': form, 'seguido': request.user.user_profile})
	else:
		form = EditarFotoForm()
	return render(request, 'editar_foto.html', {'form': form, 'seguido': request.user.user_profile}) 
 
#dar de baja a un usuario
@login_required(login_url='/')
def eliminar_usuario(request):
	usuario=Usuario.objects.get(username=request.user.username)
	username=usuario.username
	usuario.delete()
	login='0'
	return redirect(reverse('gracias', kwargs={'username': username, 'login':login}))
 

def gracias(request, username, login):
	return render(request, 'gracias.html', {'username': username, 'login': login})

#sobre mi
def sobre_mi(request):
	return render(request, 'sobre_mi.html')

