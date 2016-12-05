from motor import *
import asyncio

class DriverDosMotores(object):
	def __init__(self, motorIzq, motorDer):
		self.motorIzq = motorIzq
		self.motorDer = motorDer
		
	def Parar(self):
		self.motorIzq.Parar()
		self.motorDer.Parar()
		
	def Adelante(self):
		self.motorIzq.Adelante()
		self.motorDer.Adelante()

	def Atras(self):
		self.motorIzq.Atras()
		self.motorDer.Atras()

	def Derecha(self):
		self.motorIzq.Atras()
		self.motorDer.Adelante()
		
	def Izquierda(self):
		self.motorIzq.Adelante()
		self.motorDer.Atras()
		
	@asyncio.coroutine
	def GirarDerAsync(self):
		self.motorIzq.Atras()
		self.motorDer.Adelante()

		yield from asyncio.sleep(0.5)

		self.motorIzq.Parar()
		self.motorDer.Parar()
				
	@asyncio.coroutine
	def GirarIzqAsync(self):
		self.motorIzq.Adelante()
		self.motorDer.Atras()

		yield from asyncio.sleep(0.5)

		self.motorIzq.Parar()
		self.motorDer.Parar()
