Construcción de contenedores
============================

El proyecto incluye un ``Dockerfile`` para crear una imagen que empaqueta todas las dependencias de Cobra.
Para generar la imagen ejecuta:

.. code-block:: bash

   cobra contenedor --tag cobra

Esto ejecuta internamente ``docker build`` y produce una imagen lista para usar.

Ejecutar programas en contenedores
----------------------------------

Tras construir las imágenes es posible lanzar un script directamente en un
contenedor temporal usando ``--contenedor``:

.. code-block:: bash

   cobra ejecutar hola.co --contenedor=python
