import time
import threading

class Task( threading.Thread ):
	def __init__( self, action, loopdelay, initdelay, args ):
		self._action = action
		self._loopdelay = loopdelay
		self._initdelay = initdelay
		self._running = 1
		self._arguments = args
		threading.Thread.__init__( self )

	def run( self ):
		if self._initdelay:
			time.sleep( self._initdelay )
		self._runtime = time.monotonic()
		while self._running:
			start = time.monotonic()
			self._action(self._arguments)
			self._runtime += self._loopdelay
			time.sleep( self._runtime - start )

	def stop( self ):
		self._running = 0
	
class Scheduler:
	def __init__( self ):
		self._tasks = []
				
	def AddTask( self, action, loopdelay, initdelay = 0 , args = ""):
		task = Task( action, loopdelay, initdelay, args )
		self._tasks.append( task )
	
	def StartAllTasks( self ):
		for task in self._tasks:
			task.start()
	
	def StopAllTasks( self ):
		for task in self._tasks:
			#print ('Stopping task') 
			task.stop()
			task.join()
			#print ('Stopped')
