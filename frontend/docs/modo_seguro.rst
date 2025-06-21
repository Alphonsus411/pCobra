Modo seguro
===========

La herramienta ``cobra`` permite ejecutar programas en modo seguro mediante la
opción ``--seguro``. Esta modalidad activa el ``ValidadorSemantico`` para
revisar el AST y bloquear primitivas peligrosas como ``leer_archivo``,
``escribir_archivo``, ``obtener_url`` y ``hilo``. También restringe las
instrucciones ``import`` a los módulos instalados o listados en
``IMPORT_WHITELIST``.

Si se intenta utilizar alguna de estas operaciones se lanzará
``PrimitivaPeligrosaError`` antes de ejecutar el código.

Ejemplo de uso
--------------

.. code-block:: bash

   cobra ejecutar programa.cobra --seguro
