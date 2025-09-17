Ejemplos de Código
==================

A continuación se muestran pequeños programas escritos en Cobra que ilustran las principales características del lenguaje.

Hola Mundo
----------
.. code-block:: cobra

   imprimir("Hola, Cobra")

Manejo de holobits
------------------
.. code-block:: cobra

   var h = holobit([1.0, -0.5, 0.8])
   var proy = proyectar(h, '2D')
   graficar(proy)

Excepciones y hilos
-------------------
.. code-block:: cobra

   func tarea():
       throw "error"
   fin

   try:
       hilo tarea()
   catch e:
       imprimir(e)

Transpilación con Hololang
--------------------------
Los archivos disponibles en ``examples/hololang`` muestran cómo convertir
programas Cobra a Hololang y viceversa, además de generar salidas en Python o
ensamblador.  Ejecuta, por ejemplo:

.. code-block:: bash

   cobra compilar examples/hololang/saludo.co --backend hololang
   cobra transpilar-inverso examples/hololang/saludo.holo --origen hololang --destino python

El primer comando imprime la versión Hololang del programa ``saludo.co`` y el
segundo parte desde Hololang para reconstruir el código Python equivalente.
