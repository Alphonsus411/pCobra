Modulos nativos
===============

Cobra incluye modulos escritos en Python y JavaScript que proveen funciones
basicas para trabajar con archivos, red, operaciones matematicas y
estructuras de datos.

E/S de archivos y red
---------------------
- ``leer_archivo(ruta)`` lee el contenido de un archivo de texto.
- ``escribir_archivo(ruta, datos)`` guarda datos en un archivo.
- ``obtener_url(url)`` devuelve el texto obtenido desde una URL ``https://``.

Utilidades matematicas
----------------------
- ``sumar(a, b)`` retorna la suma de dos valores.
- ``promedio(lista)`` calcula el promedio de una lista.
- ``potencia(base, exponente)`` eleva ``base`` a ``exponente``.

Estructuras de datos
--------------------
- ``Pila`` con los metodos ``apilar`` y ``desapilar``.
- ``Cola`` con los metodos ``encolar`` y ``desencolar``.

Manejo de archivos
------------------
- ``leer(ruta)`` devuelve el contenido de un archivo.
- ``escribir(ruta, datos)`` guarda datos de texto.
- ``existe(ruta)`` comprueba si el archivo existe.
- ``eliminar(ruta)`` borra el archivo indicado.

.. code-block:: cobra

   si not existe("datos.txt"):
       escribir("datos.txt", "hola")
   imprimir(leer("datos.txt"))

Colecciones
-----------
- ``ordenar(lista)`` retorna la lista ordenada.
- ``maximo(lista)`` devuelve el mayor valor.
- ``minimo(lista)`` devuelve el menor valor.
- ``sin_duplicados(lista)`` elimina elementos repetidos.

.. code-block:: cobra

   var numeros = [3, 1, 2, 1]
   imprimir(ordenar(numeros))
   imprimir(sin_duplicados(numeros))

Operaciones numericas
---------------------
- ``es_par(n)`` indica si ``n`` es par.
- ``es_primo(n)`` verifica si ``n`` es primo.
- ``factorial(n)`` calcula el factorial de ``n``.
- ``promedio(lista)`` promedia una lista de numeros.

.. code-block:: cobra

   imprimir(es_primo(7))
   imprimir(factorial(5))

Red
---
- ``obtener_url(url, permitir_redirecciones=False)`` recupera el contenido de una URL ``https://``.
- ``enviar_post(url, datos, permitir_redirecciones=False)`` envia datos por ``POST`` a una URL ``https://``.
  Las peticiones no siguen redirecciones a menos que se habilite ``permitir_redirecciones=True``.
  Los destinos se validan opcionalmente con la lista de hosts definida en
  la variable de entorno ``COBRA_HOST_WHITELIST``. Si se permiten redirecciones,
  el host final tras la redirección también debe pertenecer a la lista blanca.

.. code-block:: cobra

   var html = obtener_url("https://ejemplo.com")

Seguridad
---------
- ``hash_sha256(texto)`` devuelve el hash SHA-256.
- ``generar_uuid()`` crea un identificador unico.

.. code-block:: cobra

   var id = generar_uuid()

Sistema
-------
- ``obtener_os()`` retorna el sistema operativo.
- ``ejecutar(args)`` ejecuta un comando en la consola a partir de una lista
  de argumentos sin pasar por un shell. Puede validarse con una lista blanca
  de comandos permitidos.
- ``obtener_env(nombre)`` lee variables de entorno.
- ``listar_dir(ruta)`` lista los archivos de un directorio.

.. code-block:: cobra

   imprimir(obtener_os())

Texto
-----
- ``mayusculas(texto)`` convierte a mayusculas.
- ``minusculas(texto)`` convierte a minusculas.
- ``invertir(texto)`` invierte el texto.
- ``concatenar(...cadenas)`` une varias cadenas.

.. code-block:: cobra

   imprimir(mayusculas("cobra"))

Tiempo
------
- ``ahora()`` devuelve la fecha y hora actual.
- ``formatear(fecha, formato)`` formatea una fecha.
- ``dormir(segundos)`` pausa la ejecucion.

.. code-block:: cobra

   dormir(1)

Estas funciones se importan automaticamente al generar código para Python
y JavaScript, por lo que pueden utilizarse directamente en el
codigo Cobra.
