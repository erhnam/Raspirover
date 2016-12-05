#!/usr/bin/env python3.4
# -*- encoding: utf-8 -*- 
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required   #para loguin
from django.contrib import auth                             #para arreglar error de login() takes exactly 1 argument (2 given)
from django.contrib.auth import authenticate, login, logout #para logout y login                                                    
from django.contrib.auth.hashers import make_password       #para password                                                            
from operator import attrgetter                             #Ordena la lista por un campo del Objeto.
from django.contrib import messages                         #para mostrar mensajes
from django.core.urlresolvers import reverse
from django.template.loader import get_template
from django.template import Context, RequestContext
from django.shortcuts import render
from django.http import HttpResponse, Http404

from .models import *
from .forms import *

from multiprocessing import Process 
from servo import *
import asyncio
import time, sys, os
import RPi.GPIO as GPIO
import picamera
import datetime
import threading
from motor import *
from camara import *
from dosMotores import *
from sensorDistancia import *
from sensorLuz import *
from sensorTemperatura import *
from sensorGas import *
from timerRecurrente import *
from subprocess import call
import datetime
import globales 

sensorDistancia=SensorDistancia(23,24)

#variables para bases de datos
dbtemperatura=sensorTemperatura()
dbhumedad=sensorHumedad()
dbgas=sensorGas()
dbluz=sensorLuz()
dbexplo=Exploracion()
trigger = ' '

def demo():
	pass

timerdth = TimerRecurrente(0, demo )
timergas = TimerRecurrente(0, demo )
timerluz = TimerRecurrente(0, demo )
trigger = TimerRecurrente(0, demo )

def index(request):
	dbtemperatura=sensorTemperatura()
	dbhumedad=sensorHumedad()
	dbgas=sensorGas()
	dbluz=sensorLuz()
	#Creacion de los motores por parejas
	motorIzq = Motor (27,22,4,100)
	motorDer = Motor (5,6,17,100)

	#Creacion del driver L298N
	globales.driver = DriverDosMotores (motorIzq, motorDer)
	
	return render(request, 'index.html')

#Funcion explorar
@login_required(login_url='/')
def explorar(request):
	global dbexplo
	global trigger
	global timerdth
	global timergas
	global timerluz
	
	if request.method == "POST":
		form = ExploracionForm(request.POST)
		if form.is_valid():
			print('Es valido')
			cleaned_data = form.cleaned_data
			globales.stemperatura = cleaned_data.get('temperatura')
			globales.shumedad = cleaned_data.get('humedad')
			globales.sgas =  cleaned_data.get('gas')
			globales.sluz =  cleaned_data.get('luz')
			globales.camara = cleaned_data.get('camara')
			tiempo = cleaned_data.get('tiempo')
			nombre = cleaned_data.get('nombre')
			descripcion = cleaned_data.get('descripcion')
	
			#usuario=Usuario.objects.get(usuario=request.user)

			dbexplo=Exploracion(nombre=nombre, tiempo=tiempo, usuariofk=request.user, descripcion=descripcion)
			
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
				if tiempo is  None:	
					timerdth = TimerRecurrente(1.0, sensordth.read)
					timerdth.start_timer()
				#Si el tiempo no es null se ejecuta el sensor segun tiempo asignado	
				else:
					timerdth = TimerRecurrente(float(tiempo)-0.2, sensordth.read)
					timerdth.start_timer()
					
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

			if globales.camara == True:
				camara_start()

			dbexplo.save()

			if tiempo is not None:
				trigger = TimerRecurrente(float(tiempo) , BBDD)
				trigger.start_timer()

			if request.method=='POST' and 'manual' in request.POST:
				return redirect(reverse('manual'))

			if request.method=='POST' and 'automatico' in request.POST:
				globales.auto=True
				return redirect(reverse('auto'))		
	else:
		form = ExploracionForm()
	context = {'form': form}
	return render(request, 'explorar.html', context)

#funcion para insertar valor de sensores en base de datos
def BBDD():
	global dbexplo

	if globales.stemperatura == True:
		dbtemperatura = temperatura(temperatura=globales.temperatura)
		dbtemperatura.save()
		dbexplo.sensores.temperatura.add(dbtemperatura)
				
	if globales.shumedad == True:
		dbhumedad = humedad(humedad=globales.humedad)
		dbhumedad.save()
		dbexplo.sensores.humedad.add(dbhumedad)

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
#	explo=Exploracion.objects.filter(usuariofk=request.user)
	explo=Exploracion.objects.all()

	context= sensorTemperatura.objects.all()
	return render(request, 'analizar.html', {'explo': explo})

@login_required(login_url='/')
def salir(request):
	global dbexplo
	global trigger
	global timerdth
	global timerluz
	global timergas

	GPIO.cleanup()
	if globales.stemperatura == True or globales.shumedad == True:
		timerdth.destroy_timer()
	if globales.sgas == True:
		timergas.destroy_timer()
	if globales.sluz == True:
		timerluz.destroy_timer()

	trigger.destroy_timer()
	camara_stop()

	del globales.driver
	

	if globales.auto == True:
		del globales.automatic
		globales.auto = False
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

