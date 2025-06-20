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
