from motor import *
import asyncio
import time

#Clase para el controlador de motor
#Recibe dos clases Motor (Costado derecho e izquierdo)
class DriverDosMotores(object):
	#Constuctor
	def __init__(self, motorIzq, motorDer):
		self.motorIzq = motorIzq
		self.motorDer = motorDer
	
	#Parar motores	
	@asyncio.coroutine
	def Parar(self):
		self.motorIzq.Parar()
		self.motorDer.Parar()

	#Motores hacia adelante	
	@asyncio.coroutine
	def Adelante(self):
		self.motorIzq.Adelante()
		self.motorDer.Adelante()
		#Gira hasta pasado este tiempo (~90º)
		yield from asyncio.sleep(0.1)
		#Para los motores
#		self.motorDer.Parar()
#		self.motorIzq.Parar()

	#Motores hacia atrás
	@asyncio.coroutine
	def Atras(self):
		self.motorIzq.Atras()
		self.motorDer.Atras()

	#Giro a la derecha
	@asyncio.coroutine
	def Derecha(self):
		self.motorDer.Atras()
		self.motorIzq.Adelante()
		#Para los motores
		time.sleep(0.15)

	#Giro a la izquierda	
	@asyncio.coroutine
	def Izquierda(self):
		self.motorDer.Adelante()
		self.motorIzq.Atras()
		time.sleep(0.15)
	
	#Giro a la derecha asincrono	
	@asyncio.coroutine
	def GirarDerAsync(self):
		self.motorDer.Atras()
		self.motorIzq.Adelante()
		#Gira hasta pasado este tiempo (~90º)
		yield from asyncio.sleep(0.5)
		#Para los motores
		self.motorDer.Parar()
		self.motorIzq.Parar()
				
	#Giro a la izquierda asincrono
	@asyncio.coroutine
	def GirarIzqAsync(self):
		self.motorDer.Adelante()
		self.motorIzq.Atras()
		#Gira hasta pasado este tiempo (~90º)
		yield from asyncio.sleep(0.5)
		#Para los motores
		self.motorIzq.Parar()
		self.motorDer.Parar()
