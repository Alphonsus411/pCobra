Modo seguro
===========

A partir de Cobra 9.0 la herramienta ``cobra`` permite ejecutar programas en
modo seguro mediante la opción ``--seguro``. Al activarse se construye una
cadena de validadores que analiza el AST y bloquea primitivas peligrosas como
``leer_archivo``, ``escribir_archivo``, ``obtener_url`` y ``hilo``.
A partir de esta versión también se restringen las funciones ``leer``,
``escribir``, ``existe`` y ``eliminar``, además de ``enviar_post`` para
operaciones de red.
El validador ``ValidadorProhibirReflexion`` impide utilizar ``eval``, ``exec`` y
otras funciones de reflexión o acceder a atributos internos como ``__dict__``.
También se valida la
instrucción ``import`` para permitir únicamente los módulos instalados o los
especificados en ``IMPORT_WHITELIST``. La instrucción ``usar`` está limitada a
los paquetes listados en ``USAR_WHITELIST`` ubicado en
``src/cobra/usar_loader.py``. Si esta lista se encuentra vacía, la
función ``obtener_modulo`` provocará un ``PermissionError`` y no se podrán
instalar dependencias nuevas.

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

   cobra ejecutar hola.co --seguro

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
``src/cobra/import_loader.py`` y ``src/cobra/usar_loader.py``
respectivamente para afinar las restricciones. Recuerda que si
``USAR_WHITELIST`` está vacía no se permitirá la instalación de paquetes
adicionales.

También es posible definir validadores adicionales creando un módulo con la
variable ``VALIDADORES_EXTRA`` y pasándolo mediante la opción
``--validadores-extra``.

Los nodos ya comprobados se almacenan en un conjunto para evitar validaciones
repetidas, lo que mejora el rendimiento cuando un mismo nodo se ejecuta varias
veces.

Para evaluar el impacto de estas comprobaciones en el rendimiento revisa
:doc:`benchmarking`.

Limitaciones de recursos
-----------------------
El modo seguro puede aplicar límites al interpretar un programa. Estos valores se
definen en ``cobra.toml`` dentro de la sección ``[seguridad]``.

.. code-block:: toml

   [seguridad]
   limite_nodos = 1000
   limite_memoria_mb = 128
   limite_cpu_segundos = 10

Si el árbol de sintaxis supera ``limite_nodos`` el intérprete aborta. Los otros
parámetros establecen el máximo de memoria en megabytes y el tiempo de CPU en
segundos usando ``limitar_memoria_mb`` y ``limitar_cpu_segundos`` de
``src.core.resource_limits``.
Esta verificación del número de nodos también se aplica al cargar módulos con
``import``.
