Modo seguro
===========

La herramienta ``cobra`` permite ejecutar programas en modo seguro mediante la
opción ``--seguro``. Al activarse se construye una cadena de validadores que
analiza el AST y bloquea primitivas peligrosas como ``leer_archivo``,
``escribir_archivo``, ``obtener_url`` y ``hilo``. También se valida la
instrucción ``import`` para permitir únicamente los módulos instalados o los
especificados en ``IMPORT_WHITELIST``.

Si se intenta utilizar alguna de estas operaciones se lanzará
``PrimitivaPeligrosaError`` antes de ejecutar el código.

Ejemplo de uso
--------------

.. code-block:: bash

   cobra ejecutar programa.cobra --seguro
