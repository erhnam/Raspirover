import threading
import globales

#Clase que crea un timer
class TimerRecurrente(threading.Timer):
    #Funcion inicial (Constructor)
	def __init__ (self, *args, **kwargs):
		threading.Timer.__init__ (self, *args, **kwargs) 
		#Inialización de variables
		self.setDaemon(True)
		self.start()
		self.running = 0

	#Funcion principal de ejecucion			
	def run(self):
		while globales.salir == 0:
			self.finished.wait (self.interval)
			self.function (*self.args, **self.kwargs)
		return

	#Función que inicia el timer
	def start_timer (self):
		self.running = 1
