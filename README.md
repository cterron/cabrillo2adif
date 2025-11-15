# Introducción
Este es un script en python 3 creado que convierte ficheros de logs en formato [Cabrillo](https://wwrof.org/cabrillo/) a formato [ADIF](https://adif.org/). Son dos tipos de formato de intercambio de información sobre QSO que utilizamos los radio aficionados.

El script se ha generado con [Copilot](https://github.com/features/copilot)  a partir de las instruccionesen español  fichero [CLAUDE.md](CLAUDE.md).

# Uso
```
cabrillo2adif.py --help
usage: cabrillo2adif.py [-h] [-i INPUT] [-o OUTPUT]

Convert Cabrillo format logs to ADIF format

options:
  -h, --help            show this help message and exit
  -i, --input INPUT     Input Cabrillo file (default: stdin)
  -o, --output OUTPUT   Output ADIF file (default: stdout)
```
El script funciona como un filtro. Si no le especificamos los ficheros de entrada (-i) o salida (-o) leeraá de la entrada estandar o escribirá en la salida estándar. Los errores siempre los escribe en la salida de error estándar.

