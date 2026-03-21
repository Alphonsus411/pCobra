Estado de los lenguajes soportados
=================================

En la actualidad Cobra puede generar código para una lista canónica de
destinos de salida: ``python``, ``rust``, ``javascript``, ``wasm``, ``go``,
``cpp``, ``java`` y ``asm``. A continuación se lista cada backend y su estado
de soporte por tier. Para más detalles consulta :doc:`frontend/backends` y la
sección *Características Principales* del `README.md <../README.md>`_.

Fuentes normativas: ``src/pcobra/cobra/transpilers/targets.py`` y ``src/pcobra/cobra/cli/target_policies.py``.

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
   * - ``cpp``
     - Tier 2
   * - Java
     - Tier 2
   * - ``asm``
     - Tier 2

Targets con runtime oficial (no equivalen a toda la transpilación)
--------------------------------------------------------------------

Los targets con runtime oficial son ``python``, ``rust``, ``javascript`` y
``cpp``. Esta categoría debe leerse por separado de la lista completa de
transpilación y de los orígenes reverse.

Orígenes reverse de entrada (no targets de salida)
--------------------------------------------------

Los siguientes lenguajes de la lista canónica reverse pueden convertirse a Cobra como **entrada** de ``cobra transpilar-inverso``. No deben confundirse con los targets oficiales de salida.

.. list-table:: Lenguajes de entrada reverse
   :header-rows: 1

   * - Lenguaje
     - Estado
   * - Python
     - Experimental
   * - JavaScript
     - Experimental
   * - Java
     - Experimental

Instalación de gramáticas
-------------------------

Para habilitar estos transpiladores inversos es necesario instalar las gramáticas de `tree-sitter`:

.. code-block:: bash

   pip install tree-sitter-languages

Este paquete incluye gramáticas para los lenguajes listados (``python``, ``javascript`` y ``java``) y puede instalarse junto con las dependencias del proyecto.

Experimentos y material separado
--------------------------------

Los pipelines o prototipos fuera del alcance oficial se conservan en ubicaciones separadas para no contaminar la política pública:

- ``docs/experimental/`` para experimentos como LLVM, reverse desde LaTeX o referencias retiradas.
- ``docs/historico/`` para material archivado sin vigencia normativa.
