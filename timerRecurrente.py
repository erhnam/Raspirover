import threading

class TimerRecurrente(threading.Timer):
     
	def __init__ (self, *args, **kwargs):
		threading.Timer.__init__ (self, *args, **kwargs) 
		self.setDaemon (True)
		self.running = 0
		self.destroy = 0
		self.start()

	def run (self):
		while True:
			self.finished.wait (self.interval)
			if self.destroy:
				return;
			if self.running:
				self.function (*self.args, **self.kwargs)

	def start_timer (self):
		self.running = 1

	def stop_timer (self):
		self.running = 0

	def is_running (self):
		return self.running

	def destroy_timer (self):
		self.destroy = 1;
