Ejemplos Avanzados
===================

En esta sección se presentan programas más complejos escritos en Cobra. Se
incluyen ejemplos con clases, uso de hilos y manejo de errores para ilustrar las
capacidades del lenguaje.

Clases
------
.. code-block:: cobra

   clase Persona:
       func __init__(self, nombre):
           self.nombre = nombre
       fin

       func saludar(self):
           imprimir("Hola, soy " + self.nombre)
       fin
   fin

   var p = Persona("Ada")
   p.saludar()

Hilos
-----
.. code-block:: cobra

   func contar():
       para var i en rango(3):
           imprimir(i)
       fin
   fin

   hilo contar()
   hilo contar()

Funciones asíncronas
--------------------
.. code-block:: cobra

   asincronico func saludo():
       imprimir("hola")
   fin

   asincronico func principal():
       esperar saludo()
   fin

   esperar principal()

Manejo de errores
-----------------
.. code-block:: cobra

   func dividir(a, b):
       si b == 0:
           throw "Division por cero"
       sino:
           return a / b
       fin
   fin

   try:
       imprimir(dividir(10, 0))
   catch e:
       imprimir("Error:" + e)
   fin

Bibliotecas C con ctypes
------------------------
.. code-block:: cobra

   var triple = cargar_funcion('libtriple.so', 'triple')
   imprimir(triple(5))
