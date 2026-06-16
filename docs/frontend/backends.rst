Soporte de backends
===================

La documentación pública de pCobra describe una sola familia de salida: **3 backends oficiales** (`python`, `javascript`, `rust`). Los targets legacy (`go`, `cpp`, `java`, `wasm`, `asm`) quedan fuera del contrato público y no se conservan como BackEnd.

.. include:: ../_generated/target_policy_summary.rst

Ejemplos de uso generados desde el registro canónico:

.. include:: ../_generated/cli_backend_examples.rst

Política de targets oficial
---------------------------

Los nombres canónicos y la clasificación por tiers se derivan de ``src/pcobra/cobra/config/transpile_targets.py`` y ``src/pcobra/cobra/transpilers/registry.py``.

.. include:: ../_generated/official_targets_table.rst

Compatibilidad explícita de Holobit SDK y librerías por target
---------------------------------------------------------------

.. include:: ../_generated/runtime_capability_matrix.rst

Alcance reverse separado
------------------------

.. include:: ../_generated/reverse_scope_table.rst
