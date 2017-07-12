from sensors import *
from globales import *
import time

spi = SPI(canalGas=2, canalLuz=3, canalBateria=1)


for i in range(0,4):
	spi.ObtenerBateria()
	print ("Globales Porcentaje: %d" % (globales.porcentaje))
	time.sleep(1)
spi.destroy()

