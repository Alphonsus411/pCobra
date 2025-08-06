Estado de los lenguajes soportados
=================================

En la actualidad Cobra puede generar código para múltiples lenguajes. A
continuación se lista cada backend y su estado de soporte. Para más
detalles consulta :doc:`../frontend/docs/backends` y la sección
*Características Principales* del `README.md <../README.md>`_.

.. list-table:: Estado de los backends
   :header-rows: 1

   * - Lenguaje
     - Estado
   * - Python
     - Estable
   * - JavaScript
     - Estable
   * - Ensamblador
     - Cobertura básica
   * - C
     - Experimental
   * - C++
     - Experimental
   * - Rust
     - Parcial
   * - WebAssembly
     - Experimental
   * - Go
     - Parcial
   * - Kotlin
     - Parcial
   * - Swift
     - Parcial
   * - R
     - Parcial
   * - Julia
     - Parcial
   * - Java
     - Parcial
   * - COBOL
     - Parcial
   * - Fortran
     - Parcial
   * - Pascal
     - Parcial
   * - VisualBasic
     - Parcial
   * - Ruby
     - Parcial
   * - PHP
     - Parcial
   * - Perl
     - Parcial
   * - Matlab
     - Parcial
   * - Mojo
     - Parcial
   * - LaTeX
     - Parcial

Transpiladores inversos
-----------------------

Los siguientes lenguajes pueden convertirse a Cobra:

.. list-table:: Lenguajes de entrada
   :header-rows: 1

   * - Lenguaje
     - Estado
   * - Ensamblador
     - Experimental
   * - C
     - Experimental
   * - C++
     - Experimental
   * - COBOL
     - Experimental
   * - Fortran
     - Experimental (tree-sitter)
   * - Go
     - Experimental
   * - Java
     - Experimental
   * - JavaScript
     - Experimental
   * - Julia
     - Experimental
   * - Kotlin
     - Experimental
   * - LaTeX
     - Experimental
   * - Matlab
     - Experimental
   * - Mojo
     - Experimental
   * - Pascal
     - Experimental
   * - Perl
     - Experimental
   * - PHP
     - Experimental
   * - Python
     - Experimental
   * - R
     - Experimental
   * - Ruby
     - Experimental
   * - Rust
     - Experimental
   * - Swift
     - Experimental
   * - VisualBasic
     - Experimental (tree-sitter)
   * - WebAssembly
     - Experimental

Instalación de gramáticas
-------------------------

Para habilitar estos transpiladores inversos es necesario instalar las gramáticas de `tree-sitter`:

.. code-block:: bash

   pip install tree-sitter-languages

Este paquete incluye gramáticas para los lenguajes listados y puede instalarse junto con las dependencias del proyecto.

Para conocer el alcance y las limitaciones del soporte de LaTeX consulte :doc:`soporte_latex`.

