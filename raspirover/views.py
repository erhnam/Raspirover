# -*- encoding: utf-8 -*-
########################## LIBRERÍAS ###############################

from django.utils import timezone
from django.db import transaction
#para graficas Chartit2
from chartit import DataPool, Chart

from django.contrib import messages
#Renders de Django
from django.shortcuts import render, redirect, render_to_response
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
from django.urls import reverse
#Librería timeimport time
from datetime import datetime
#Librería para controlar GPIO
import RPi.GPIO as GPIO
#Libreria para hilos
import threading
#Libreria para Max, min y avg
from django.db.models import Avg, Max, Min

#Importaciones de ficheros creados para sensores, camara, motores y globales.
import globales
from .models import *
from .forms import *
from sensors.servo import *
from sensors.camara import *
from sensors.driver import *
from sensors.laser import *
from timer import *
from sensores import *

########################## PINES GPIO ##########################

H298N1IN1 = 12 #ADELANTE DER
H298N1IN2 = 17 #ADELANTE DER
H298N1IN3 = 27 #ADELANTE IZQ
H298N1IN4 = 22 #ADELANTE IZQ

H298N2IN1 = 5 #MEDIO IZQ
H298N2IN2 = 6 #MEDIO IZQ
H298N2IN3 = 13
H298N2IN4 = 26

H298N3IN1 = 18
H298N3IN2 = 23
H298N3IN3 = 24
H298N3IN4 = 25

S1 = Servo(0)
S3 = Servo(1)
S4 = Servo(2)
S6 = Servo(3)

S1.setup()
S3.setup()
S4.setup()
S6.setup()

M1 = Motor(H298N1IN1,H298N1IN2)
M2 = Motor(H298N2IN1,H298N2IN2)
M3 = Motor(H298N3IN1,H298N3IN2)
M4 = Motor(H298N3IN3,H298N3IN4)
M5 = Motor(H298N2IN3,H298N2IN4)
M6 = Motor(H298N1IN3,H298N1IN4)

LASERPIN = 4

sensors = Sensors(15) #15 segundos

sensors.start()

driver = Driver(M1,M2,M3,M4,M5,M6,S1,S3,S4,S6)

driver.Parar()

laser = Laser(LASERPIN)
laser.setup()

########################## MANAGER DE TAREAS ##########################

scheduler = Scheduler()

########################## VOLTAJE ##########################

#spi = SPI(canalGas = SENSORGAS, canalLuz = SENSORLUZ, canalFuego = SENSORFUEGO)

#bateria = Task( 59.0 , spi.ObtenerBateria )
#bateria.start_timer()

#Creacion de los Servos


########################## INICIO  ###############################

#pagina principal donde inicias sesion
def base(request):
	# Si el usuario esta ya logueado, lo redireccionamos a index
	if request.user.is_authenticated:
		return render(request, 'index.html')

	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				#logeamos al usuario
				login(request, user)
				#redireccionamos a la pagina de inicio de la partida
				return redirect(reverse('index'))
			else:
				# Redireccionar informando que la cuenta esta inactiva
				messages.error(request, 'Tu cuenta de usuario esta inactiva')
		messages.error(request, 'Nombre de usuario o contraseña no valido')
	return render(request, 'login.html')


#funcion para apagar el sistema
def apagar(request):
	os.system("sudo poweroff")

#funcion para reiniciar el sistema
def reboot(request):
	os.system("sudo reboot")

#Función de la página principal del programa
def index(request):

	#global servoHor
	#global servoVer
	salir(request)

	#Centra la camara
	#servoHor.center()
	#servoVer.center()

	servo_c()

	return render(request, 'index.html')

#Funcion que accede a la página Analizar
@login_required(login_url='index')
def analizar(request):
	request.session['salir']=True

	#extraer todas las exploraciones del usuario
	explo=Exploracion.objects.filter(usuariofk=request.user)

	return render(request, 'analizar.html', {'explo': explo})

#Funcion que ofrece las opciones para iniciar una exploración
@login_required(login_url='index')
def explorar(request):

	global scheduler
	global sensors

	#Si es método post
	if request.method == "POST":
		#se crea un formulaio
		form = ExploracionForm(request.POST)
		#Si el formulario es válido
		if form.is_valid():
			#Se extraen los valores del formulario
			cleaned_data = form.cleaned_data
			request.session['tiempo'] = 30.0
			nombre = cleaned_data.get('nombre')
			descripcion = cleaned_data.get('descripcion')

			request.session['tiempo'] = float(request.session['tiempo'])
			dbexplo = Exploracion(nombre=nombre, tiempo=request.session['tiempo'], usuariofk=request.user, descripcion=descripcion)
			dbexplo.save()

			scheduler.AddTask( request.session['tiempo'], BBDD, args=[request, dbexplo.id_exploracion] )

			request.session['dbexplo'] = dbexplo.id_exploracion

			#Se crea una tabla sensor de temperatura asociado a la exploracion
			dbtemperatura = Sensor(tipo="Temperatura", enable=True)
			dbtemperatura.save()
			dbexplo.sensores.add(dbtemperatura)

			dbhumedad = Sensor(tipo="Humedad", enable=True)
			dbhumedad.save()
			dbexplo.sensores.add(dbhumedad)

			dbluz = Sensor(tipo="Luz", enable=True)
			dbluz.save()
			dbexplo.sensores.add(dbluz)

			dbgas = Sensor(tipo="Gas", enable=True)
			dbgas.save()
			dbexplo.sensores.add(dbgas)

			dbpresion = Sensor(tipo="Presion", enable=True)
			dbpresion.save()
			dbexplo.sensores.add(dbpresion)

			#Se crea un timer de x segundos definidos por la variable tiempo

			camara_start()

			scheduler.StartAllTasks()

			return redirect('manual')

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
			valor = Lecturas.objects.create(dato=luz, fecha=start, sensor=sensor)

			valor = Lecturas.objects.create(dato=gas, fecha=start, sensor=sensor)

			valor = Lecturas.objects.create(dato=presion, fecha=start, sensor=sensor)

			valor = Lecturas.objects.create(dato=temperatura, fecha=start, sensor=sensor)

			valor = Lecturas.objects.create(dato=humedad, fecha=start, sensor=sensor)

	end = datetime.now()
	diff = end - sta
	elapsed_ms = (diff.days * 86400000) + (diff.seconds * 1000) + (diff.microseconds / 1000)

#Elimina una exploración elegida por el usuario
@login_required(login_url='index')
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

			elif sensor.tipo == "Presion":
				s = Sensor.objects.get(exploracion=explo, tipo="Presion")
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
	p = "Presion"

	#extraer solo la exploracion seleccionada
	explo = Exploracion.objects.get(pk=id_exploracion)
	#extraer los sensores utilizados en la exploracion
	sensores = Sensor.objects.filter(exploracion=explo)

	context = {'explo':explo, 't':t, 'h':h, 'l':l, 'g':g, 'p':p, 'sensores' : sensores }

	return render(request, 'detalleExploracion.html', context)

#Funcion que muestra una gráfica seleccionada
@login_required(login_url='index')
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
@login_required(login_url='index')
def mostrarGrafica (request, id_exploracion, sensor_tipo):
	#con sensor_tipo se sabe la gráfica que se ha seleccionado
	explo = Exploracion.objects.get(pk=id_exploracion)

	if sensor_tipo == "Temperatura":

		titulo = "Gráfica de la exploración " + explo.nombre + " de Temperatura" 

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

		titulo = "Gráfica de la exploración " + explo.nombre + " de Humedad" 

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

		titulo = "Gráfica de la exploración " + explo.nombre + " de Gas" 

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

	#Se ha seleccionado gráfica de Fuego
	elif sensor_tipo == "Presion":

		titulo = "Gráfica de la exploración " + explo.nombre + " de Presion" 

		sensor =  Sensor.objects.get(exploracion=explo, tipo="Presion")

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

		titulo = "Gráfica de la exploración " + explo.nombre + " de Luz" 

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
@login_required(login_url='index')
def salir(request):

	global scheduler

	#Destruye los timers
	request.session['salir'] = True

	#Para el Manager del sistema
	scheduler.StopAllTasks()

	#Para la camara
	camara_parar()

	request.session['salir'] = False

	#Inicializacion de variables
	inicializar()

	#redirige al index
	return redirect('index')

#Función que muestra el porcentaje del voltaje de la pila
#En la pantalla de control del sistema
@login_required(login_url='index')
def mostrarvoltaje(request):

	context = {'voltaje': porcentaje}

	template = "base.html"
	return render(request, template, context)

#Función que muestra los datos de los sensores en pantalla modo de control
#En la pantalla de control del sistema
@login_required(login_url='index')
def mostrardatos(request):

	context = {'temperatura': globales.temperatura, 'humedad': globales.humedad, 'gas' : globales.gas, 'luz' : globales.luz, 'presion' : globales.presion}

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
@login_required(login_url='index')
def manual(request):
	global driver
	global laser
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
			laser.on()

		#Disminuir velocidad
		elif (control == "sdown"):
			laser.off()

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


#Funcion que registra a un usuario en el sitema
def registro(request):

	#Si el formulario ha sido enviado
	if request.method=='POST':
		#Se vinculan los datos POST con el formulario UsuarioForm
		form = UsuarioForm(request.POST,request.FILES)

		#Si el formulario pasa todas las reglas de validacion se recogen los datos y se procesan")
		if form.is_valid():
			email=form.cleaned_data['email']
#			photo = form.cleaned_data.get('photo')
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
def login(request, user):
	#Comprueba autentificación del usuario
	if request.user.is_authenticated:
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
def logout(request):
	auth.logout(request)
	return redirect(reverse('base'))

#Función para editar contraseña
@login_required(login_url='index')
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
@login_required(login_url='index')
def editar_foto(request):
	#Se obtiene el usuario
	usuario=request.user  
	if request.method == 'POST':
		#Crea formulario
		form = EditarFotoForm(request.POST, request.FILES)
		#Comprueba formulario
		if form.is_valid():
			#Realiza cambios
			request.user.photo = form.cleaned_data['imagen']
			request.user.save()
			return render(request, 'editar_foto.html', {'form': form, 'usuario': usuario})
	else:
		form = EditarFotoForm()
	return render(request, 'editar_foto.html', {'form': form, 'usuario': usuario}) 

#Función para  dar de baja a un usuario
@login_required(login_url='index')
def eliminar_usuario(request):
	#Se busca usuario
	usuario=request.user
	username = usuario.username
	#Se borra usuario de la base de datos
	usuario.delete()
	login='0'
	return redirect(reverse('gracias', kwargs={'username': username, 'login':login}))

#Función para dar las gracias cuando inícias, cierras o borras usuario
def gracias(request, username, login):
	return render(request, 'gracias.html', {'username': username, 'login': login})

#Función para sobre mi
def sobre_mi(request):
	return render(request, 'sobre_mi.html')
