Manejo de la caché de AST y tokens
==================================

La caché incremental usa **SQLitePlus** para almacenar AST completos, tokens y
fragmentos. Por defecto se crea la base de datos en ``~/.cobra/sqliteplus/core.db``
y es obligatorio definir la variable de entorno ``SQLITE_DB_KEY`` antes de usar
la CLI. Puedes cambiar la ruta exportando ``COBRA_DB_PATH``::

   export SQLITE_DB_KEY="clave-local"
   export COBRA_DB_PATH="$HOME/.cobra/sqliteplus/core.db"

.. note::
   ``COBRA_AST_CACHE`` permanece como alias de compatibilidad. Al definirla,
   se derivará una ruta ``cache.db`` dentro del directorio indicado y se emitirá
   una advertencia de obsolescencia.

Nombre y extensiones
--------------------

Los registros se indexan por el SHA256 del código fuente. El comando guarda el
AST completo y los tokens asociados dentro de tablas SQLite, evitando archivos
intermedios en disco.

Fragmentos reutilizables
------------------------

Los fragmentos utilizados por el parser también se almacenan en la base. Cada
fragmento se identifica con el hash del código sobre el que se calculó, lo que
permite reutilizarlos entre compilaciones.

Limpieza de la base
-------------------

Para eliminar todas las entradas y recompac tar la base utiliza::

   cobra cache --vacuum

Migración desde JSON
--------------------

Si aún conservas archivos ``.ast`` y ``.tok`` del esquema anterior, impórtalos
con el script auxiliar incluido en ``scripts/``::

   python scripts/migrar_cache_sqliteplus.py --origen /ruta/a/cache

El script recorre los hashes existentes, los inserta en SQLitePlus y deja la
base lista para reutilizar la caché sin repetir el análisis.
