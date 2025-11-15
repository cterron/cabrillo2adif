# Introducción
Este es un script en python creado que convierte ficheros de logs en formato [Cabrillo](https://wwrof.org/cabrillo/) a formato [ADIF](https://adif.org/). Son dos tipos de formato de intercambio de información sobre QSO que utilizamos los radio aficionados.

El script se ha generado con [Copilot](https://github.com/features/copilot)  a partir de las instruccionesen español  fichero [CLAUDE.md](CLAUDE.md).

# Uso
```
cabrillo2adif.py [-i input_file] [-o output_file]
```
El script funciona como un filtro. Si no le especificamos los ficheros de entrada (-i) o salida (-o) leeraá de la entrada estandar o escribirá en la salida estándar. Los errores siempre los escribe en la salida de error estándar.

