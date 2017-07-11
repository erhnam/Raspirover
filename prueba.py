from sensors import *
from globales import *

spi = SPI(canalLuz=1)

spi.ObtenerLuz()

print(globales.luz)

spi.destroy()
