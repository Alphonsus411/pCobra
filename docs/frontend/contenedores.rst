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
- ``cobra-javascript``
- ``cobra-cpp``
- ``cobra-rust``

Política de ejecución Docker vs transpilación oficial
-----------------------------------------------------

Cobra distingue explícitamente entre dos alcances:

- **Targets oficiales de transpilación**: ``python``, ``rust``, ``javascript``, ``wasm``, ``go``, ``cpp``, ``java`` y ``asm``.
- **Targets oficiales con runtime Docker**: ``python``, ``javascript``, ``cpp`` y ``rust``.

Los targets ``go``, ``java``, ``wasm`` y ``asm`` se mantienen como destinos de
**transpilación oficial** y no se publican como runtimes Docker oficiales.
En consecuencia, no hay Dockerfiles dedicados para su ejecución directa en contenedor.

Ejecutar programas en contenedores
----------------------------------

Tras construir las imágenes es posible lanzar un script directamente en un
contenedor temporal usando ``--contenedor``:

.. code-block:: bash

   cobra ejecutar hola.co --contenedor=python

La opción ``--contenedor`` solo acepta los runtimes Docker oficiales anteriores;
no debe interpretarse como paridad automática con todos los targets de generación.
