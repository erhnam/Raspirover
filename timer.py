import threading
import globales

#Clase que crea un timer
class Task(threading.Timer):
	#Funcion inicial (Constructor)
	def __init__ (self, *args, **kwargs):
		threading.Timer.__init__ (self, *args, **kwargs) 
		self.setDaemon(True)
		self.running = 0

	#Funcion principal de ejecucion			
	def run(self):
		while self.running == 1:
			self.finished.wait (self.interval)
			self.function (*self.args, **self.kwargs)
		return

	#Función que inicia el timer
	def start_timer (self):
		self.running = 1
		self.start()

	#Función que inicia el timer
	def stop (self):
		globales.salir=1
		self.running = 0


#Manejador de Tareas    
class Scheduler(object):
	def __init__( self ):
		self._tasks = []

	#Funcion que añade las tareas
	def AddTask( self, *args, **kwargs):
		task = Task( *args, **kwargs )
		self._tasks.append( task )

	#Funcion que ejecuta todas las tareas
	def StartAllTasks( self ):
		for task in self._tasks:
			task.start_timer()

	#Funcion que para y borra todas las tareas
	def StopAllTasks( self ):
		for task in self._tasks:
			task.stop()

		#Vacía la lista de tareas
		self._tasks.clear()

