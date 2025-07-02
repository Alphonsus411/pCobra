Modo seguro
===========

La herramienta ``cobra`` permite ejecutar programas en modo seguro mediante la
opción ``--seguro``. Al activarse se construye una cadena de validadores que
analiza el AST y bloquea primitivas peligrosas como ``leer_archivo``,
``escribir_archivo``, ``obtener_url`` y ``hilo``.
A partir de esta versión también se restringen las funciones ``leer``,
``escribir``, ``existe`` y ``eliminar``, además de ``enviar_post`` para
operaciones de red.
El validador ``ValidadorProhibirReflexion`` impide utilizar ``eval``, ``exec`` y
otras funciones de reflexión o acceder a atributos internos como ``__dict__``.
También se valida la
instrucción ``import`` para permitir únicamente los módulos instalados o los
especificados en ``IMPORT_WHITELIST``. La instrucción ``usar`` está limitada a
los paquetes listados en ``USAR_WHITELIST`` ubicado en
``backend/src/cobra/usar_loader.py``.

La cadena comienza con ``ValidadorAuditoria`` que registra mediante
``logging.warning`` cada primitiva utilizada. Esta auditoría puede
habilitarse o deshabilitarse editando ``cobra.toml``:

.. code-block:: toml

   [auditoria]
   activa = true

Si se intenta utilizar alguna de estas operaciones se lanzará
``PrimitivaPeligrosaError`` antes de ejecutar el código.

Ejemplo de uso
--------------

.. code-block:: bash

   cobra ejecutar programa.co --seguro

Validadores personalizados
-------------------------
Se puede ampliar la cadena de validación pasando la opción
``--validadores-extra`` con la ruta a un módulo que defina la lista
``VALIDADORES_EXTRA``. Cada elemento debe ser una instancia de un validador.

.. code-block:: bash

   cobra ejecutar programa.co --seguro --validadores-extra mis_validadores.py

Configuraciones avanzadas
-------------------------

Las listas ``IMPORT_WHITELIST`` y ``USAR_WHITELIST`` determinan qué módulos y
paquetes pueden cargarse cuando el modo seguro está activo. Puedes editarlas en
``backend/src/cobra/import_loader.py`` y ``backend/src/cobra/usar_loader.py``
respectivamente para afinar las restricciones.

También es posible definir validadores adicionales creando un módulo con la
variable ``VALIDADORES_EXTRA`` y pasándolo mediante la opción
``--validadores-extra``.

Para evaluar el impacto de estas comprobaciones en el rendimiento revisa
:doc:`benchmarking`.
