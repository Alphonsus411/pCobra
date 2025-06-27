Soporte de backends
===================

Cobra permite generar código para varios lenguajes a través del subcomando
``compilar``. A partir de esta versión se incluye un backend experimental para
WebAssembly.

Para obtener el código en formato WAT basta ejecutar:

.. code-block:: bash

   cobra compilar programa.co --backend wasm

El resultado puede compilarse posteriormente con herramientas como
``wat2wasm`` para obtener un módulo ejecutable.
