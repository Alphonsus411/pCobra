Manual de Referencia de Cobra
=============================

Esta sección describe brevemente las palabras clave y funciones integradas del lenguaje.

Palabras clave
--------------
- ``var``: declara variables.
- ``func``: define funciones.
- ``rel``: crea funciones relativas a un contexto temporal.
- ``si`` / ``sino``: condicionales.
- ``mientras`` / ``para``: bucles de control.
- ``import``: carga otros archivos Cobra.
- ``try`` / ``catch`` / ``throw``: manejo de excepciones.
- ``hilo``: ejecuta una función en un hilo concurrente.

Funciones integradas
--------------------
- ``imprimir(valor)``: muestra ``valor`` por la salida estándar.
- ``holobit(lista)``: construye un holobit a partir de una lista.
- ``proyectar(h, modo)``: proyecta un holobit en ``modo`` (por ejemplo ``'2D'``).
- ``transformar(h, accion, valor)``: aplica una transformación sobre un holobit.
- ``graficar(h)``: visualiza el holobit en pantalla.

Uso de la CLI
-------------
El comando ``cobra`` cuenta con varias subopciones:

.. code-block:: bash

   cobra compilar archivo.cobra --tipo python
   cobra ejecutar archivo.cobra --depurar
   cobra modulos listar
   cobra docs

La opción ``--seguro`` puede añadirse a ``ejecutar`` o al modo interactivo para
bloquear primitivas peligrosas e importaciones no permitidas.

El subcomando ``docs`` genera la documentación del proyecto en ``frontend/build/html``.
