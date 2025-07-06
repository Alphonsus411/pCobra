Manejo de la cach\u00e9 del AST
=============================

La compilaci\u00f3n de archivos Cobra genera árboles de sintaxis abstracta
(AST) que se guardan para acelerar futuras ejecuciones.

.. note::
   La cach\u00e9 usa un **checksum** del c\u00f3digo (SHA256) para nombrar los
   archivos. Puedes modificar la ruta predeterminada con la variable de
   entorno ``COBRA_AST_CACHE``.

Nombre de los archivos
----------------------

Cada archivo del directorio de cach\u00e9 recibe por nombre el SHA256
calculado a partir del c\u00f3digo fuente original y se almacena con
extensi\u00f3n ``.ast``.

Variable de entorno ``COBRA_AST_CACHE``
---------------------------------------

Por defecto la cach\u00e9 se coloca en ``cache`` dentro de la ra\u00edz del
proyecto. Puedes cambiar esta ubicaci\u00f3n definiendo la variable de
entorno ``COBRA_AST_CACHE`` antes de ejecutar la compilaci\u00f3n.

Limpiar la cach\u00e9
------------------

Para eliminar todos los archivos ``.ast`` existe el subcomando:

.. code-block:: bash

   cobra cache

que borra los ficheros generados e informa por pantalla que la cach\u00e9 ha
sido limpiada.
