Construcción de contenedores
============================

El proyecto incluye un ``Dockerfile`` para crear una imagen que empaqueta todas las dependencias de Cobra.
Para generar la imagen ejecuta:

.. code-block:: bash

   cobra contenedor --tag cobra

Esto ejecuta internamente ``docker build`` y produce una imagen lista para usar.

Imágenes Docker soportadas
--------------------------

El script ``docker/scripts/build.sh`` construye estas imágenes de ejecución en contenedor:

- ``cobra``
- ``cobra-python``
- ``cobra-js``
- ``cobra-cpp``
- ``cobra-rust``

Política para Tier 2/wasm/asm en Docker
---------------------------------------

Los targets ``wasm`` y ``asm``, así como ``go`` y ``java`` (Tier 2), se mantienen
como destinos de **transpilación** y no se publican como runtimes Docker oficiales.
En consecuencia, no hay Dockerfiles dedicados para su ejecución directa en contenedor.

Ejecutar programas en contenedores
----------------------------------

Tras construir las imágenes es posible lanzar un script directamente en un
contenedor temporal usando ``--contenedor``:

.. code-block:: bash

   cobra ejecutar hola.co --contenedor=python
