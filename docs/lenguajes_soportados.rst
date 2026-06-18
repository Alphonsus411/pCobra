Estado de los lenguajes soportados
=================================

Esta guía mantiene una sola narrativa pública: pCobra transpila públicamente únicamente a **3 backends oficiales** (``python``, ``javascript`` y ``rust``) y separa con claridad la lista de targets de salida, el estado de runtime y la compatibilidad contractual de Holobit/SDK.

Resumen normativo derivado automáticamente desde la política canónica:

.. include:: _generated/target_policy_summary.rst

Fuentes normativas visibles:

- ``src/pcobra/cobra/architecture/backend_policy.py`` (``PUBLIC_BACKENDS``) para la lista pública canónica y el orden contractual.
- ``src/pcobra/cobra/cli/target_policies.py`` para la separación entre transpilación, runtime oficial, runtime best-effort y compatibilidad SDK.
- ``src/pcobra/cobra/transpilers/compatibility_matrix.py`` para el estado contractual de Holobit, ``corelibs`` y ``standard_library``.

Lista exacta de targets oficiales
---------------------------------

.. include:: _generated/official_targets_table.rst

Resumen por tier
----------------

- **Tier 1 público**: ``python``, ``javascript`` y ``rust``.
- **Legacy interno/histórico**: cualquier target retirado se documenta solo en anexos internos/históricos y no forma parte de la superficie pública.

Capacidades públicas por backend
--------------------------------

.. include:: _generated/runtime_capability_matrix.rst

Interpretación oficial:

- ``python`` es el único backend con compatibilidad SDK completa y estado Holobit ``full``.
- ``rust`` y ``javascript`` tienen runtime oficial verificable y adaptador Holobit mantenido por el proyecto, pero siguen en estado contractual ``partial``.
- Las referencias históricas o rutas internas de migración/regresión no tienen runtime Docker oficial público ni contrato de salida público.

Transpilación inversa (feature independiente)
---------------------------------------------

La transpilación inversa es una capacidad separada de los backends de salida. El destino final público debe ser uno de ``python``, ``javascript`` o ``rust``; cualquier origen histórico adicional se documenta solo en anexos internos/históricos.

.. code-block:: bash

   cobra transpilar-inverso script.py --origen=python --destino=javascript

Esta funcionalidad debe documentarse como **origen reverse de entrada**, no como ampliación de la lista oficial de targets de salida.

Comparativa contractual
-----------------------

La cobertura pública por backend se resume en la matriz contractual principal:

.. include:: matriz_transpiladores.md

La tabla anterior debe leerse literalmente: un backend en estado ``partial`` puede generar hooks, adaptadores o imports contractuales, pero eso **no** equivale automáticamente a runtime oficial verificable ni a compatibilidad SDK completa.
