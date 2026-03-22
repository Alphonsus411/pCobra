Estado de los lenguajes soportados
=================================

En la actualidad Cobra puede generar código para la lista canónica de destinos de salida definida por la política pública. A continuación se incluye el estado oficial derivado automáticamente desde dicha fuente normativa. Para más detalles consulta :doc:`frontend/backends` y la sección *Características Principales* del `README.md <../README.md>`_.

Fuentes normativas: ``src/pcobra/cobra/transpilers/targets.py`` y ``src/pcobra/cobra/cli/target_policies.py``.

.. include:: _generated/official_targets_table.rst

Targets con runtime oficial (no equivalen a toda la transpilación)
--------------------------------------------------------------------

Los targets con runtime oficial son ``python``, ``rust``, ``javascript`` y ``cpp``. Esta categoría debe leerse por separado de la lista completa de transpilación y de los orígenes reverse.

Runtime experimental/best-effort conservado en tooling auxiliar
---------------------------------------------------------------

Algunos artefactos auxiliares y tests conservan cobertura best-effort para
``go`` y ``java``. Estos nombres siguen formando parte de la **transpilación
oficial**, pero no deben confundirse con runtime oficial de CLI/sandbox.

Targets de transpilación sin runtime público en esta capa
---------------------------------------------------------

Los targets ``wasm`` y ``asm`` siguen siendo oficiales para generar código,
pero en la política pública actual no se presentan como runtimes ejecutables
ni como runtimes experimentales dentro de la suite auxiliar.

Orígenes reverse de entrada (no targets de salida)
--------------------------------------------------

Los siguientes lenguajes de la lista canónica reverse pueden convertirse a Cobra como **entrada** de ``cobra transpilar-inverso``. No deben confundirse con los targets oficiales de salida.

.. include:: _generated/reverse_scope_table.rst

Instalación de gramáticas
-------------------------

Para habilitar estos transpiladores inversos es necesario instalar las gramáticas de `tree-sitter`:

.. code-block:: bash

   pip install tree-sitter-languages

Este paquete incluye gramáticas para los lenguajes listados (``python``, ``javascript`` y ``java``) y puede instalarse junto con las dependencias del proyecto.

Experimentos y material separado
--------------------------------

Los pipelines o prototipos fuera del alcance oficial se conservan en ubicaciones separadas para no contaminar la política pública:

- ``archive/retired_targets/`` para material histórico retirado del árbol principal.
- ``docs/historico/`` para glosarios o notas archivadas que sigan siendo parte de la documentación del repositorio.
