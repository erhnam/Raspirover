from motor import *
import asyncio
import time
import globales

#Clase para el controlador de motor
#Recibe dos clases Motor (Costado derecho e izquierdo)
class DriverDosMotores(object):
	#Constuctor
	def __init__(self, motorIzq, motorDer):
		self.motorIzq = motorIzq
		self.motorDer = motorDer
	
	#Ajusta la velocidad de los motores
	def SetSpeed (self,speed):
		if (speed >= 100):
			globales.velocidad = 100
			self.motorDer.SetSpeed(100)
			self.motorIzq.SetSpeed(100)
		elif (speed <= 10 ):
			globales.velocidad = 20
			self.motorDer.SetSpeed(20)
			self.motorIzq.SetSpeed(20)
		else:
			globales.velocidad = speed
			self.motorDer.SetSpeed(speed)
			self.motorIzq.SetSpeed(speed)

	#Parar motores	
	def Parar(self):
		self.motorIzq.Parar()
		self.motorDer.Parar()
		time.sleep(0.1)

	#Motores hacia adelante	
	def Adelante(self):
		self.motorIzq.Adelante()
		self.motorDer.Adelante()
		time.sleep(0.1)

	#Motores hacia atrás
	def Atras(self):
		self.motorIzq.Atras()
		self.motorDer.Atras()
		time.sleep(0.1)

	#Giro a la derecha
	def Derecha(self):
		self.motorDer.Atras()
		self.motorIzq.Adelante()
		time.sleep(0.1)

	#Giro a la izquierda	
	def Izquierda(self):
		self.motorDer.Adelante()
		self.motorIzq.Atras()
#		time.sleep(0.001)
	
	#Giro a la derecha asincrono	
	@asyncio.coroutine
	def GirarDerAsync(self):
		self.motorDer.Atras()
		self.motorIzq.Adelante()
		#Gira hasta pasado este tiempo (~90º)
		yield from asyncio.sleep(0.48)
		#Para los motores
		self.motorDer.Parar()
		self.motorIzq.Parar()
				
	#Giro a la izquierda asincrono
	@asyncio.coroutine
	def GirarIzqAsync(self):
		self.motorDer.Adelante()
		self.motorIzq.Atras()
		#Gira hasta pasado este tiempo (~90º)
		yield from asyncio.sleep(0.48)
		#Para los motores
		self.motorIzq.Parar()
		self.motorDer.Parar()
