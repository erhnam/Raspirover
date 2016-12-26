
#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

########################## LIBRERÍAS ###############################

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

#Importaciones de ficheros creados para
#sensores, camara, motores y globales.
from .models import *
from .forms import *
from servo import *
from motor import *
from camara import *
from dosMotores import *
from sensores import *
from timerRecurrente import *
import globales 

########################## CONTROLADOR ###############################

#Creacion de los motores por parejas
motorIzq = Motor (27,22,4,100)
motorDer = Motor (5,6,17,100)

#Creacion del driver L298N
globales.driver = DriverDosMotores (motorIzq, motorDer)	

########################## INICIO  ###############################

#Función de la página principal del programa
def index(request):
	#reinicia todas las variables	
	inicializar()
	
	#Se inicializa los puertos GPIO
	print("index:")
	print(globales.salir)
	setup(14,23,21,20,16,26)
	return render(request, 'index.html')

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
			tiempo = cleaned_data.get('tiempo')
			nombre = cleaned_data.get('nombre')
			descripcion = cleaned_data.get('descripcion')
	
			#Se crea una exploracion con parte de los valores del formulario
			#Si tiempo no está vacío se crea una exploracion	
			if tiempo is not None:
				dbexplo=Exploracion(nombre=nombre, tiempo=tiempo, usuariofk=request.user, descripcion=descripcion)
				dbexplo.save()
			
			#Se ha elegido en el formulario el sensor de temperatura o humedad (es el mismo)			
			if globales.stemperatura == True or globales.shumedad == True:
				#Se crea una tabla sensor de temperatura asociado a la exploracion
				if globales.stemperatura == True and tiempo is not None:
					dbtemperatura = sensorTemperatura(tipo="Temperatura", enable=True)
					dbtemperatura.save()
					dbexplo.sensores.add(dbtemperatura)

				#Se crea una tabla sensor de humedad asociada a la exploracion	
				if globales.shumedad == True and tiempo is not None:
					dbhumedad = sensorHumedad(tipo="Humedad", enable=True)
					dbhumedad.save()
					dbexplo.sensores.add(dbhumedad)

				#Si el tiempo es null se ejecuta el sensor cada 5 segundos			
				if tiempo is None:	
					timerdth = TimerRecurrente(5.0, comprobarth)
					timerdth.start_timer()
				#Si el tiempo no es null se crea un timer de x segundos definidos por la variable tiempo
				else:
					timerdth = TimerRecurrente(float(tiempo)-0.2, comprobarth)
					timerdth.start_timer()
			
			#Se ha elegido en el formulario el sensor de luz		
			if globales.sluz == True:
				#Se crea sensor de Luz para manejar con Raspberry
				sensorluz = SensorLuz(21,20,16)
				#Se crea un timer de x segundos definidos por la variable tiempo
				if tiempo is not None:	
					#Se crea una tabla sensor de luz asociada a la exploracion	
					dbluz = sensorLuz(tipo="Luz", enable=True)
					dbluz.save()
					dbexplo.sensores.add(dbluz)
					#Se crea un timer de x segundos definidos por la variable tiempo
					timerluz = TimerRecurrente(float(tiempo)-0.2, sensorluz.comprobarLuz)
					timerluz.start_timer()
				#Si el tiempo es null se ejecuta el sensor cada 5 segundos	
				else:
					#Se crea un timer de 5 segundos
					timerluz = TimerRecurrente(5.0, sensorluz.comprobarLuz)
					timerluz.start_timer()

			#Se ha elegido en el formulario el sensor de gas
			if globales.sgas == True:
				#Se crea sensor de gas (MQ-2) para manejar con Raspberry
				sensorgas = SensorGas(26)
				#Si el tiempo no es null se ejecuta el sensor segun tiempo asignado	
				if tiempo is not None:
					#Se crea una tabla sensor de gas asociada a la exploracion	
					dbgas = sensorGas(tipo="Gas", enable=True)
					dbgas.save()
					dbexplo.sensores.add(dbgas)
					#Se crea un timer de x segundos definidos por la variable tiempo
					timergas = TimerRecurrente(float(tiempo)-0.2, sensorgas.comprobarGas)
					timergas.start_timer()
				#Si el tiempo es null se ejecuta el sensor cada 5 segundos			
				else:
					#Se crea un timer de 5 segundos
					timergas = TimerRecurrente(5.0, sensorgas.comprobarGas)
					timergas.start_timer()

			#Si se ha elegido cámara para streaming
			if globales.camara == True:
				camara_start()
			
			#Si se ha insertado tiempo se lanza un trigger para la bbdd
			#definida por la variable tiempo
			if tiempo is not None:
				trigger = TimerRecurrente(float(tiempo) , BBDD, args=[dbexplo.id_exploracion])
				trigger.start_timer()

			#Si se ha elegido manual
			if request.method=='POST' and 'manual' in request.POST:				
				return redirect(reverse('manual'))

			#si se ha elegido automatico
			if request.method=='POST' and 'automatico' in request.POST:
				#Sirve para cancelar el modo automatico
				globales.auto=True
				return redirect(reverse('auto'))

	else:
		form = ExploracionForm()
	context = {'form': form}
	return render(request, 'explorar.html', context)

#funcion para insertar valor de sensores en base de datos
def BBDD(id_exploracion):

	#Se busca la exploracion actual
	dbexplo = Exploracion.objects.get(pk=id_exploracion)

	#Si está activado el sensor de temperatura
	if globales.stemperatura == True:
		#Se añade un nuevo valor de temperatura a la base de datos
		dbtemperatura = sensorTemperatura(temperatura=globales.temperatura, tipo="Temperatura", enable=True)
		dbtemperatura.save()
		dbexplo.sensores.add(dbtemperatura)

	#Si está activado el sensor de humedad
	if globales.shumedad == True:
		#Se añade un nuevo valor de humedad a la base de datos
		dbhumedad = sensorHumedad(humedad=globales.humedad, tipo="Humedad", enable=True)
		dbhumedad.save()
		dbexplo.sensores.add(dbhumedad)

	#Si está activado el sensor de gas
	if globales.sgas == True:
		#Se añade un nuevo valor de gas a la base de datos
		dbgas = sensorGas(gas=globales.gas, tipo="Gas")
		dbgas.save()
		dbexplo.sensores.add(dbgas)

	#Si está activado el sensor de luz
	if globales.sluz == True:
		#Se añade un nuevo valor de luz a la base de datos
		dbluz = sensorLuz(luz=globales.luz, tipo="Luz")
		dbluz.save()
		dbexplo.sensores.add(dbluz)

#Funcion que accede a la página Analizar
@login_required(login_url='/')
def analizar(request):
	#extraer todas las exploraciones del usuario
	explo=Exploracion.objects.filter(usuariofk=request.user)

	return render(request, 'analizar.html', {'explo': explo})

#Elimina una exploración elegida por el usuario
@login_required(login_url='/')
def eliminarExploracion(request, id_exploracion):
	#Busca la exploracion
	explo = Exploracion.objects.get(pk=id_exploracion)
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

#Funcion que muestra una gráfica seleccionada
@login_required(login_url='/')
def mostrarGrafica (request, id_exploracion, sensor_tipo):
	#con sensor_tipo se sabe la gráfica que se ha seleccionado
	explo = Exploracion.objects.get(pk=id_exploracion)
	#Se ha seleccionado gráfica de temperatura
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

	#Se ha seleccionado gráfica de humedad
	if sensor_tipo == "Humedad":
		titulo = "Gráfica de la exploracion " + explo.nombre + " de Humedad" 
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

	#Se ha seleccionado gráfica de Gas
	if sensor_tipo == "Gas":
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
		context = {'sensor':sensor, 'chart': cht, 'tipo': sensor_tipo ,'explo' : explo}

		return render(request, 'mostrarGrafica.html', context)

	#Se ha seleccionado gráfica de Luz
	if sensor_tipo == "Luz":
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
		context = {'sensor':sensor, 'chart': cht, 'tipo': sensor_tipo ,'explo' : explo}

		return render(request, 'mostrarGrafica.html', context)

#Funcion para salir del modo de control
@login_required(login_url='/')
def salir(request):

	#Destruye los timers
	globales.salir=1
	
	#Para la cámara
	camara_stop()

	#si estaba en automático
	if globales.auto == True:
		#borra hilo de automático
		del globales.automatic

	#redirige al index
	return redirect('index')

#Función que muestra los datos de los sensores en pantalla modo de control
#En la pantalla de control del sistema
@login_required(login_url='/')
def mostrardatos(request):
	context = {'temperatura': globales.temperatura, 'humedad': globales.humedad, 'gas' : globales.gas, 'luz' : globales.luz, 
	'stemp' : globales.stemperatura, 'shum' : globales.shumedad, 'sgas' : globales.sgas, 'sluz' : globales.sluz, 'camara':globales.camara }

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

#Función de control manual del sistema
@login_required(login_url='/')
def manual(request):

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

	#Corta el hilo			
	return

#FUncion que llama al control automatico
@login_required(login_url='/')
def auto(request):
	#Indica que está el modo automatico activado
	globales.auto=True	
	#Creamos un hilo para ejecutar el automatico
	#así no bloquea a los demas hilos
	globales.automatic=threading.Thread(target=automatico)
	globales.automatic.start()

	#creamos el contexto
	context = {'temperatura': globales.temperatura, 'humedad': globales.humedad, 'gas' : globales.gas, 'luz' : globales.luz, 
	'stemp' : globales.stemperatura, 'shum' : globales.shumedad, 'sgas' : globales.sgas, 'sluz' : globales.sluz, 'camara':globales.camara }
	
	template = "auto.html"
	return render_to_response(template, context, context_instance=RequestContext(request))
	
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
				return render_to_response('registro.html',{'form':form}, context_instance=RequestContext(request))
		
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
	
	return render_to_response('registro.html',{'form':form}, context_instance=RequestContext(request))


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

