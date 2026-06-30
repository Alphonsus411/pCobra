Paquetes Cobra
==============

Un paquete Cobra publicable usa la extensión ``.co`` y se distribuye como un
contenedor ZIP. El contenedor conserva la estructura de carpetas del proyecto,
incluye un manifiesto ``cobra.pkg.json`` y registra checksums SHA-256 para los
archivos empaquetados.

Este formato pertenece a la capa de herramientas de empaquetado y CobraHub: no
modifica la sintaxis del lenguaje ni requiere cambios en el Lexer o el Parser.
Los archivos fuente Cobra pueden seguir usando ``.cobra`` o ``.co``; cuando
``.co`` se usa como paquete publicable, la CLI lo trata como un ZIP con
metadatos.

Contenido soportado
-------------------

Los paquetes ``.co`` pueden incluir:

* archivos fuente ``.cobra`` y ``.co``;
* documentación ``.md``;
* archivos de texto ``.txt``;
* ``Dockerfile``;
* recursos adicionales preservando sus rutas relativas.

Manifiesto ``cobra.pkg.json``
-----------------------------

El manifiesto ``cobra.pkg.json`` describe los metadatos del paquete y la lista de
archivos incluidos. Cada entrada se acompaña de su checksum SHA-256 para que las
operaciones de validación e inspección puedan detectar cambios o corrupción del
contenedor.

Ejemplo simplificado:

.. code-block:: json

   {
     "nombre": "demo",
     "version": "0.1.0",
     "archivos": [
       {
         "ruta": "main.co",
         "sha256": "..."
       },
       {
         "ruta": "README.md",
         "sha256": "..."
       }
     ]
   }

Flujo recomendado
-----------------

Crear la estructura inicial del paquete:

.. code-block:: bash

   cobra paquete crear mi_paquete --nombre demo --version 0.1.0

Construir el contenedor publicable ``.co``:

.. code-block:: bash

   cobra paquete construir mi_paquete dist/demo.co

Validar checksums y manifiesto:

.. code-block:: bash

   cobra paquete validar dist/demo.co

Inspeccionar los metadatos y archivos incluidos:

.. code-block:: bash

   cobra paquete inspeccionar dist/demo.co

Extraer el paquete en una carpeta local:

.. code-block:: bash

   cobra paquete extraer dist/demo.co ./vendor/demo

Compatibilidad con comandos legacy
----------------------------------

Los comandos legacy, como ``cobra paquete instalar`` y las variantes antiguas de
``cobra paquete crear`` con salida posicional, se conservan como alias de
compatibilidad. Para paquetes nuevos, el formato recomendado es el contenedor
``.co`` con manifiesto ``cobra.pkg.json`` y checksums SHA-256.

Véase también
-------------

* :doc:`../cobrahub_paquetes`
* La sección "Paquetes ``.co`` y CobraHub" del ``README.md`` del repositorio.
