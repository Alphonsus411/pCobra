Estado de los lenguajes soportados
=================================

En la actualidad Cobra puede generar código para una lista canónica de
destinos de salida. A continuación se lista cada backend y su estado de
soporte por tier. Para más detalles consulta :doc:`frontend/backends` y la
sección *Características Principales* del `README.md <../README.md>`_.

Fuente de verdad: ``src/pcobra/cobra/transpilers/targets.py``.

.. list-table:: Estado de los backends
   :header-rows: 1

   * - Lenguaje
     - Estado
   * - Python
     - Tier 1
   * - Rust
     - Tier 1
   * - JavaScript
     - Tier 1
   * - WebAssembly
     - Tier 1
   * - Go
     - Tier 2
   * - C++
     - Tier 2
   * - Java
     - Tier 2
   * - Ensamblador
     - Tier 2

Transpiladores inversos
-----------------------

Los siguientes lenguajes de la lista canónica pueden convertirse a Cobra:

.. list-table:: Lenguajes de entrada
   :header-rows: 1

   * - Lenguaje
     - Estado
   * - Python
     - Experimental
   * - Rust
     - Experimental
   * - JavaScript
     - Experimental
   * - WebAssembly
     - Experimental
   * - Go
     - Experimental
   * - C++
     - Experimental
   * - Java
     - Experimental
   * - Ensamblador
     - Experimental

Instalación de gramáticas
-------------------------

Para habilitar estos transpiladores inversos es necesario instalar las gramáticas de `tree-sitter`:

.. code-block:: bash

   pip install tree-sitter-languages

Este paquete incluye gramáticas para los lenguajes listados y puede instalarse junto con las dependencias del proyecto.
