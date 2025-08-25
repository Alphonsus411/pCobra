Manual de Referencia de Cobra
=============================

Esta sección describe brevemente las palabras clave y funciones integradas del lenguaje.

Palabras clave
--------------
- ``var``: declara variables.
- ``func``: define funciones.
- ``si`` / ``sino``: condicionales.
- ``mientras`` / ``para``: bucles de control.
- ``import``: carga otros archivos Cobra.
- ``try`` / ``catch`` / ``throw``: manejo de excepciones.
- ``hilo``: ejecuta una función en un hilo concurrente.
- ``asincronico`` / ``esperar``: define funciones asíncronas y espera su resultado.

Funciones integradas
--------------------
- ``imprimir(valor)``: muestra ``valor`` por la salida estándar.
- ``holobit(lista)``: construye un holobit a partir de una lista.
- ``proyectar(h, modo)``: proyecta un holobit en ``modo`` (por ejemplo ``'2D'``).
- ``transformar(h, accion, valor)``: aplica una transformación sobre un holobit.
- ``graficar(h)``: visualiza el holobit en pantalla.
- ``escalar(h, factor)``: multiplica las coordenadas por ``factor``.
- ``mover(h, x, y, z)``: traslada el holobit en el espacio.
  Estas funciones están disponibles en ``holobit-sdk`` desde la versión ``1.0.8``;
  en versiones anteriores Cobra realiza el cálculo de forma interna.

Uso de la CLI
-------------
El comando ``cobra`` cuenta con varias subopciones:

.. code-block:: bash

   cobra compilar archivo.co --tipo python
   cobra compilar archivo.co --tipo asm
   cobra compilar archivo.co --tipo ruby
   cobra compilar archivo.co --tipo php
   cobra ejecutar archivo.co --depurar
   cobra modulos listar
   cobra docs
   cobra empaquetar --output dist

El modo seguro está habilitado por defecto. Si se desea permitir primitivas
peligrosas e importaciones no permitidas, puede desactivarse con ``--no-seguro``
en ``ejecutar`` o en el modo interactivo.

El subcomando ``docs`` genera la documentación del proyecto en ``frontend/build/html``.
``empaquetar`` crea un ejecutable independiente usando PyInstaller.
