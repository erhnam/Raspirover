import threading
import globales

#Clase que crea un timer
class TimerRecurrente(threading.Timer):
    #Funcion inicial (Constructor)
	def __init__ (self, *args, **kwargs):
		threading.Timer.__init__ (self, *args, **kwargs) 
		#Inialización de variables
		self.setDaemon (True)
		self.running = 0
		self.destroy = 0
		self.start()

	#Funcion principal de ejecucion			
	def run (self):
		#Mientras no se active salir seguirá ejecutando
		while globales.salir == 0:
			self.finished.wait (self.interval)
			
			#Se destruye el timer
			if self.destroy:
				return;

			#Sigue ejecutándose
			if self.running:
				self.function (*self.args, **self.kwargs)

			if globales.salir == 1:
				self.destroy = 1;
				return;

	#Función que inicia el timer
	def start_timer (self):
		self.running = 1

	#Función que para el timer
	def stop_timer (self):
		self.running = 0

	#Función que devuelve el valor de running
	def is_running (self):
		return self.running

	#Función que devuelve el valor de destroy
	def destroy_timer (self):
		self.destroy = 1;
