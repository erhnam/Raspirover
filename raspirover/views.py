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


def index(request):
	#Creacion de los motores por parejas
	motorIzq = Motor (27,22,4,70)
	motorDer = Motor (5,6,17,70)

	#Creacion del driver L298N
	globales.driver = DriverDosMotores (motorIzq, motorDer)
	
	return render(request, 'index.html')

#Funcion explorar
@login_required
def explorar(request):

	sensor=' '
	
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
	
			usuario=request.user.user_profile

			explo=Exploracion(nombre=nombre, tiempo=tiempo, usuario=usuario, descripcion=descripcion)

			if globales.stemperatura == True or globales.shumedad == True:
				sensordth = SensorTemperatura(14)	
				timerdth = TimerRecurrente(float(tiempo)-0.2, sensordth.read)
				timerdth.start_timer()
				if globales.stemperatura == True:
					globales.dbtemperatura=SensorTemperatura()
					globales.dbtemperatura.enable=True
					globales.dbtemperatura.save()
					explo.sensorTemperatura=globales.dbtemperatura
				if globales.shumedad == True:
					globales.dbhumedad=SensorHumedad()
					globales.dbhumedad.enable=True					
					globales.dbhumedad.save()
					explo.sensorHumedad=globales.dbhumedad

			if globales.sgas == True:
				sensorgas = SensorGas(26)
				timerluz = TimerRecurrente(float(tiempo)-0.2, sensorgas.comprobarGas)
				timerluz.start_timer()
				globales.dbgas=SensorGas()
				globales.dbgas.enable=True
				globales.dbgas.save()
				explo.sensorGas=globales.dbgas

			if globales.sluz == True:
				sensorluz = SensorLuz(21,20)
				timergas = TimerRecurrente(float(tiempo)-0.2, sensorluz.comprobarLuz)
				timergas.start_timer()
				globales.dbluz=SensorLuz()
				globales.dbluz.enable=True
				globales.dbluz.save()
				explo.sensorLuz=globales.dbluz

			if globales.camara == True:
				camara_start()

			if tiempo == True:
				trigger = TimerRecurrente(float(tiempo), BBDD)
				trigger.start_timer()
				globales.dbtiempo.save()
				explo.tiempo=globales.dbtiempo

			explo.save()
			
			if request.method=='POST' and 'manual' in request.POST:
				return redirect(reverse('manual'))

			if request.method=='POST' and 'automatico' in request.POST:
				globales.auto=True
				globales.sensordistancia = SensorDistancia(23,24)
				return redirect(reverse('auto'))		
	else:
		form = ExploracionForm()
	context = {'form': form}
	return render(request, 'explorar.html', context)

#funcion para insertar valor de sensores en base de datos
def BBDD():
	if globales.stemperatura == True:
		dbtemperatura.add(temperatura=globales.temperatura)
	if globales.shumedad == True:
		dbhumedad.add(humedad=globales.humedad)
	if globales.sgas == True:
		dbgas.add(gas=globales.gas)
	if globales.sluz == True:
		dbluz.add(luz=globales.luz)

#funcion Analizar
@login_required
def analizar(request):
	return render(request, 'analizar.html')

@login_required
def salir(request):
	del globales.driver
	if globales.auto == True:
		del globales.automatic
	globales.inicializar()
	return redirect(reverse('index'))

@login_required
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
	sensorDistancia = globales.sensordistancia
	
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
@login_required
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
	
	print("entro en modo auto")
	sensorDistancia = globales.sensordistancia
	
	#Comienzo de la automatización
	while True:
		
		globales.distancia = float( sensorDistancia.precisionDistancia() - 20 )	
		print ("Distancia: %.2f" % globales.distancia)
		if globales.distancia < 30.0:
			BuscarDistanciaMasLarga()
		else:
			globales.driver.Adelante()


@login_required
def auto(request):

	context = {'temperatura': globales.temperatura, 'humedad': globales.humedad, 'gas' : globales.gas, 'luz' : globales.luz, 
	'stemp' : globales.stemperatura, 'shum' : globales.shumedad, 'sgas' : globales.sgas, 'sluz' : globales.sluz, 'camara':globales.camara }

	globales.automatic=threading.Thread(target=automatico)
	globales.automatic.start()
					
	template = "auto.html"
	return render(request, template, context)


#registrar usuario
def registro(request):
	if request.method == 'POST':
		form = RegistroUserForm(request.POST, request.FILES)
 
		if form.is_valid():
			cleaned_data = form.cleaned_data
			username = cleaned_data.get('username')
			password = cleaned_data.get('password')
			email = cleaned_data.get('email')
			photo = cleaned_data.get('photo')
			user_model = User.objects.create_user(username=username, password=password)
			user_model.email = email
			user_model.save()
			user_profile = UserProfile()
			user_profile.user = user_model
			user_profile.photo = photo
			user_profile.save()
			return redirect(reverse('gracias', kwargs={'username': username}))
	else:
		form = RegistroUserForm()
	context = {'form': form}
	return render(request, 'registro.html', context)

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
@login_required
def logout(request):
	try:
		del request.session['member_id']
	except KeyError:
		pass
	return redirect('/')

#editar contraseña
@login_required
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
@login_required
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
@login_required
def eliminar_usuario(request):
	usuario=User.objects.get(username=request.user.username)
	username=usuario.username
	usuario.delete()
	login='0'
	return redirect(reverse('gracias', kwargs={'username': username, 'login':login}))
 

def gracias(request, username, login):
	return render(request, 'gracias.html', {'username': username, 'login': login})

#sobre mi
def sobre_mi(request):
	return render(request, 'sobre_mi.html')

