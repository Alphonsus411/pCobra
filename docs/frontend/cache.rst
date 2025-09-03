Manejo de la caché de AST y tokens
==================================

La compilación de archivos Cobra genera árboles de sintaxis abstracta
(AST) y tokens que se guardan en formato JSON para acelerar futuras
ejecuciones.

.. note::
   La caché usa un **checksum** del código (SHA256) para nombrar los
   archivos. Puedes modificar la ruta predeterminada con la variable de
   entorno ``COBRA_AST_CACHE``.

Nombre y extensiones de los archivos
------------------------------------

Cada archivo del directorio de caché recibe por nombre el SHA256
calculado a partir del código fuente original. Los AST se almacenan
como JSON con extensión ``.ast`` y los tokens con extensión ``.tok``.

Fragmentos reutilizables
------------------------

Además de estos archivos, existe el subdirectorio ``cache/fragmentos``
que guarda fragmentos intermedios que pueden reutilizarse entre
compilaciones.

Variable de entorno ``COBRA_AST_CACHE``
---------------------------------------

Por defecto la caché se coloca en ``cache`` dentro de la raíz del
proyecto. Puedes cambiar esta ubicación definiendo la variable de
entorno ``COBRA_AST_CACHE`` antes de ejecutar la compilación. Esta
variable afecta tanto a los archivos ``.ast`` y ``.tok`` como al
subdirectorio ``cache/fragmentos``.

Limpiar la caché
----------------

Para eliminar todos los archivos ``.ast`` y ``.tok`` junto con los
fragmentos almacenados, existe el subcomando:

.. code-block:: bash

   cobra cache

que borra los ficheros generados e informa por pantalla que la caché ha
sido limpiada.
