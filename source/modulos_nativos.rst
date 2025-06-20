Modulos nativos
===============

Cobra incluye modulos escritos en Python y JavaScript que proveen funciones
basicas para trabajar con archivos, red, operaciones matematicas y
estructuras de datos.

E/S de archivos y red
---------------------
- ``leer_archivo(ruta)`` lee el contenido de un archivo de texto.
- ``escribir_archivo(ruta, datos)`` guarda datos en un archivo.
- ``obtener_url(url)`` devuelve el texto obtenido desde una URL.

Utilidades matematicas
----------------------
- ``sumar(a, b)`` retorna la suma de dos valores.
- ``promedio(lista)`` calcula el promedio de una lista.
- ``potencia(base, exponente)`` eleva ``base`` a ``exponente``.

Estructuras de datos
--------------------
- ``Pila`` con los metodos ``apilar`` y ``desapilar``.
- ``Cola`` con los metodos ``encolar`` y ``desencolar``.

Estas funciones se importan automaticamente al transpilar tanto a Python
como a JavaScript, por lo que pueden utilizarse directamente en el
codigo Cobra.
