#Variables globales
lon=None			#inicializa las variable de longitud
lat=None			#inicializa la variable del latitud
voltaje=0.0			#Inicializa el voltaje a 0.0 v
porcentaje=0.0		#Inicializa el valor del voltaje a 0 %
salir=0				#Controla la salida del modo auto o manual
driver=None			#Controlador del motor
dbexplo=None		#Base de datos de exploracion
dbtemperatura=None	#Base de datos de temperatura
dbhumedad=None		#Base de datos de humedad
dbgas=None			#Base de datos de gas
dbfuego=None		#Base de datos de fuego
dbluz=None			#Base de datos de luz
dbgps=None			#Base de datos de gps
dbtiempo=None		#Base de datos de tiempo
distancia=0.0		#Distancia proporcionada por el sensor
temperatura=0.0		#Valor de la temperatura
humedad=0.0			#Valor de la humedad
gas=0				#Valor de gas
co=0				#Valor de CO
smoke=0				#Valor de humo
fuego=0				#Valor de fuego
luz=0				#Valor de luz
trigger=None		#Trigger para almacenar los datos
auto=False      	#Variable para detectar modo automatico
manu=False			#Variables para detectar modo manual
cam=None
automatic=None		#Variable que carga hilo de modo automatico
manual=None			#Variable que carga hilo de modo manual
sdistancia=False    #Variable del sensor distancia del formulario 
stemperatura=False  #Variable del sensor temperatura del formulario
shumedad=False      #Variable del sensor humedad del formulario
sgas=False          #Variable del sensor gas del formulario
sfuego=False        #Variable del sensor fuego del formulario
sluz=False          #Variable del sensor luz del formulario
sgps=False			#Variable del sensor gps del formulario
camara=False        #Variable de la camara del formulario
tiempo=None        	#Variable de tiempo del formulario 
nombre=False        #Variable del nombre del formulario
velocidad=30		#Variable que indica la velocidad del robot

#Funcion que inicializa las variables
def inicializar():
	lon=None			#inicializa las variable de longitud
	lat=None			#inicializa la variable del latitud
	voltaje=0.0			#Inicializa el voltaje a 0.0 v
	porcentaje=0.0		#Inicializa el valor del voltaje a 0 %
	salir=0				#Controla la salida del modo auto o manual
	driver=None			#Controlador del motor
	dbexplo=None		#Base de datos de exploracion
	dbtemperatura=None	#Base de datos de temperatura
	dbhumedad=None		#Base de datos de humedad
	dbgas=None			#Base de datos de gas
	dbfuego=None		#Base de datos de fuego
	dbluz=None			#Base de datos de luz
	dbgps=None			#Base de datos de gps
	dbtiempo=None		#Base de datos de tiempo
	distancia=0.0		#Distancia proporcionada por el sensor
	temperatura=0.0		#Valor de la temperatura
	humedad=0.0			#Valor de la humedad
	gas=0				#Valor de gas
	co=0				#Valor de CO
	smoke=0				#Valor de humo
	fuego=0				#Valor de fuego
	luz=0				#Valor de luz
	trigger=None		#Trigger para almacenar los datos
	auto=False      	#Variable para detectar modo automatico
	manu=False			#Variables para detectar modo manual
	cam=None			#Variable para detectar la camara
	automatic=None		#Variable que carga hilo de modo automatico
	manual=None			#Variable que carga hilo de modo manual
	sdistancia=False    #Variable del sensor distancia del formulario 
	stemperatura=False  #Variable del sensor temperatura del formulario
	shumedad=False      #Variable del sensor humedad del formulario
	sgas=False          #Variable del sensor gas del formulario
	sfuego=False        #Variable del sensor fuego del formulario
	sluz=False          #Variable del sensor luz del formulario
	sgps=False			#Variable del sensor gps del formulario
	camara=False        #Variable de la camara del formulario
	tiempo=None        	#Variable de tiempo del formulario 
	nombre=False        #Variable del nombre del formulario
	velocidad=30		#Variable que indica la velocidad del robot
