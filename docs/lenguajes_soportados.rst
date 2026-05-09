Estado de los lenguajes soportados
=================================

Esta guía mantiene una sola narrativa pública: pCobra transpila únicamente a **8 backends oficiales** y separa con claridad la lista de targets de salida, el estado de runtime y la compatibilidad contractual de Holobit/SDK.

Resumen normativo derivado automáticamente desde la política canónica:

.. include:: _generated/target_policy_summary.rst

Fuentes normativas visibles:

- ``src/pcobra/cobra/config/transpile_targets.py`` para la lista canónica y los tiers.
- ``src/pcobra/cobra/cli/target_policies.py`` para la separación entre transpilación, runtime oficial, runtime best-effort y compatibilidad SDK.
- ``src/pcobra/cobra/transpilers/compatibility_matrix.py`` para el estado contractual de Holobit, ``corelibs`` y ``standard_library``.

Lista exacta de targets oficiales
---------------------------------

.. include:: _generated/official_targets_table.rst

Resumen por tier
----------------

- **Tier 1**: ``python``, ``rust``, ``javascript`` y ``wasm``.
- **Tier 2**: ``go``, ``cpp``, ``java`` y ``asm``.

Capacidades públicas por backend
--------------------------------

.. include:: _generated/runtime_capability_matrix.rst

Interpretación oficial:

- ``python`` es el único backend con compatibilidad SDK completa y estado Holobit ``full``.
- ``rust`` y ``javascript`` tienen runtime oficial verificable y adaptador Holobit mantenido por el proyecto, pero siguen en estado contractual ``partial``.
- ``go`` y ``java`` conservan runtime best-effort no público (sin runtime Docker oficial).
- ``wasm`` y ``asm`` son backends oficiales de salida orientados a transpilación, no a runtime oficial público ni Docker oficial.
- ``cpp`` permanece como backend legacy/internal sin runtime Docker oficial público.

Transpilación inversa (feature independiente)
---------------------------------------------

La transpilación inversa es una capacidad separada de los backends de salida. Los orígenes soportados hoy son ``python``, ``javascript`` y ``java``; el destino final debe ser uno de los 8 backends oficiales de salida.

.. code-block:: bash

   cobra transpilar-inverso script.py --origen=python --destino=javascript

Esta funcionalidad debe documentarse como **origen reverse de entrada**, no como ampliación de la lista oficial de targets de salida.

Comparativa contractual
-----------------------

La cobertura pública por backend se resume en la matriz contractual principal:

.. include:: matriz_transpiladores.md

La tabla anterior debe leerse literalmente: un backend en estado ``partial`` puede generar hooks, adaptadores o imports contractuales, pero eso **no** equivale automáticamente a runtime oficial verificable ni a compatibilidad SDK completa.
