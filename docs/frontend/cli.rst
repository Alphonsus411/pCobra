CLI de Cobra
===========

La CLI pública de Cobra se enfoca en un flujo estable para usuario final con
cinco comandos:

- ``cobra run archivo.cobra``
- ``cobra build archivo.cobra``
- ``cobra test archivo.cobra``
- ``cobra mod ...``
- ``cobra repl``

Estos comandos exponen la UX oficial. La selección de backend, adaptación de
runtime y detalles de transpilación quedan encapsulados dentro de la
arquitectura interna.

Política pública de backends
----------------------------

.. include:: ../_generated/target_policy_summary.rst

Ejemplos de backends públicos generados desde el registro canónico:

.. include:: ../_generated/cli_backend_examples.rst

Flujo público recomendado
-------------------------

Ejecutar un programa:

.. code-block:: bash

   cobra run archivo.cobra

Construir artefactos:

.. code-block:: bash

   cobra build archivo.cobra

Ejecutar pruebas del proyecto o de un archivo:

.. code-block:: bash

   cobra test archivo.cobra

Gestionar módulos:

.. code-block:: bash

   cobra mod list
   cobra mod install paquete.cobra
   cobra mod remove paquete.cobra

Architecture overview (resumen corto)
--------------------------------------

Diagrama principal:

.. code-block:: text

   Frontend Cobra
        ↓
   BackendPipeline
        ↓
   Bindings (python/javascript/rust)

- ``Frontend Cobra`` analiza el código y produce AST.
- ``BackendPipeline`` resuelve backend y normaliza compilación interna.
- ``Bindings`` conecta con runtime oficial en Python, JavaScript y Rust.

Imports y biblioteca estándar (resolución determinista)
-------------------------------------------------------

La resolución de imports en la ruta pública es determinista y prioriza el
espacio estándar antes de rutas híbridas ambiguas. Para documentación y ejemplos
se usan los módulos canónicos:

- ``cobra.core``
- ``cobra.datos``
- ``cobra.web``
- ``cobra.system``

