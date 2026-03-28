Soporte de backends
===================

La documentación pública de pCobra describe una sola familia de salida: **8 backends oficiales** agrupados en Tier 1 y Tier 2.

.. include:: ../_generated/target_policy_summary.rst

Ejemplos de uso generados desde el registro canónico:

.. include:: ../_generated/cli_backend_examples.rst

Política de targets oficial
---------------------------

Los nombres canónicos y la clasificación por tiers de estos backends se derivan de ``src/pcobra/cobra/config/transpile_targets.py`` y ``src/pcobra/cobra/transpilers/registry.py``.

Esto describe la **salida oficial de transpilación**, no una promesa uniforme de ejecución. Para evitar drift documental, el estado por backend se inyecta desde artefactos generados:

.. include:: ../_generated/official_targets_table.rst

La separación entre salida oficial y runtime se mantiene explícita y vigente:

- **targets oficiales de salida (8)**: ``python``, ``rust``, ``javascript``, ``wasm``, ``go``, ``cpp``, ``java`` y ``asm``;
- **runtime oficial verificable**: ``python``, ``rust``, ``javascript`` y ``cpp``;
- **runtime best-effort**: ``go`` y ``java``;
- **solo transpilación**: ``wasm`` y ``asm``;
- **SDK full**: solo ``python``.

Política de soporte por tiers (SLA)
-----------------------------------

- **Tier 1** (``python``, ``rust``, ``javascript``, ``wasm``): triage inicial de regresiones <= 2 días hábiles.
- **Tier 2** (``go``, ``cpp``, ``java``, ``asm``): triage inicial de regresiones <= 5 días hábiles.

La promoción/degradación entre tiers requiere RFC aprobada, plan de migración y comunicación en changelog/notas de release.

Compatibilidad explícita de Holobit SDK y librerías por target
---------------------------------------------------------------

.. list-table::
   :header-rows: 1

   * - Target
     - Tier
     - Holobit SDK
     - corelibs
     - standard_library
   * - ``python``
     - Tier 1
     - ``full`` (requiere ``holobit-sdk``)
     - ``full``
     - ``full``
   * - ``rust``
     - Tier 1
     - ``partial``
     - ``partial``
     - ``partial``
   * - ``javascript``
     - Tier 1
     - ``partial``
     - ``partial``
     - ``partial``
   * - ``wasm``
     - Tier 1
     - ``partial`` (host-managed)
     - ``partial`` (host-managed)
     - ``partial`` (host-managed)
   * - ``go``
     - Tier 2
     - ``partial`` (best-effort)
     - ``partial``
     - ``partial``
   * - ``cpp``
     - Tier 2
     - ``partial`` (adaptador mantenido)
     - ``partial``
     - ``partial``
   * - ``java``
     - Tier 2
     - ``partial`` (best-effort)
     - ``partial``
     - ``partial``
   * - ``asm``
     - Tier 2
     - ``partial`` (inspección/diagnóstico)
     - ``partial``
     - ``partial``

Migración desde targets retirados
---------------------------------

Para proyectos históricos que dependían de targets eliminados, utiliza la guía oficial:

- ``docs/migracion_targets_retirados.md``

Matriz de características
-------------------------

Para un resumen completo de la cobertura contractual por backend, revisa la matriz de transpiladores:

.. include:: ../../docs/matriz_transpiladores.md

Comandos válidos por destino
----------------------------

Listado generado desde el registro canónico para evitar desalineaciones entre documentación y CLI.
Las guías públicas deben usar la nomenclatura canónica de flags: ``--backend`` (equivalente operativo de ``--tipo``) y ``--tipos`` para listas.

.. include:: ../_generated/cli_backend_examples.rst
