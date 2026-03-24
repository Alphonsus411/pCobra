Soporte de backends
===================

La documentación pública de pCobra describe una sola familia de salida: **8 backends oficiales** agrupados en Tier 1 y Tier 2.

.. include:: ../_generated/target_policy_summary.rst

Ejemplos de uso generados desde el registro canónico:

.. include:: ../_generated/cli_backend_examples.rst

Política de targets oficial
---------------------------

Los nombres canónicos y la clasificación por tiers de estos backends se derivan de ``src/pcobra/cobra/transpilers/targets.py`` y ``src/pcobra/cobra/transpilers/registry.py``.

Esto describe la **salida oficial de transpilación**, no una promesa uniforme de ejecución. Para evitar drift documental, el estado por backend se inyecta desde artefactos generados:

.. include:: ../_generated/official_targets_table.rst

Matriz de características
-------------------------

Para un resumen completo de la cobertura contractual por backend, revisa la matriz de transpiladores:

.. include:: ../../docs/matriz_transpiladores.md

Comandos válidos por destino
----------------------------

Listado generado desde el registro canónico para evitar desalineaciones
entre documentación y CLI:

.. include:: ../_generated/cli_backend_examples.rst
