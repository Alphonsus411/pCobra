Estado de los lenguajes soportados
=================================

La narrativa pública de pCobra es única: el proyecto transpila a **8 backends oficiales** y los organiza en **Tier 1** y **Tier 2**. La lista canónica y el reparto por tiers se derivan de ``src/pcobra/cobra/config/transpile_targets.py``; la política de runtime, Holobit y SDK se deriva de ``src/pcobra/cobra/cli/target_policies.py``.

.. include:: _generated/official_targets_table.rst

Estado público de runtime, Holobit y SDK
----------------------------------------

.. include:: _generated/runtime_capability_matrix.rst

Lectura correcta de la política pública:

- Los backends oficiales de salida son únicamente ``python``, ``rust``, ``javascript``, ``wasm``, ``go``, ``cpp``, ``java`` y ``asm``.
- El runtime oficial verificable solo cubre ``python``, ``rust``, ``javascript`` y ``cpp``.
- ``go`` y ``java`` conservan runtime best-effort no público; ``wasm`` y ``asm`` son targets oficiales de solo transpilación.
- La compatibilidad SDK completa solo puede prometerse para ``python``.
- El soporte Holobit debe leerse siempre junto con la matriz contractual: ``python`` es ``full``; el resto de backends oficiales permanecen en ``partial``.

Orígenes reverse de entrada (no targets de salida)
--------------------------------------------------

Los siguientes lenguajes pertenecen al alcance reverse como **entrada** de ``cobra transpilar-inverso``. No son targets oficiales adicionales de salida.

.. include:: _generated/reverse_scope_table.rst

Instalación de gramáticas
-------------------------

Para habilitar estos transpiladores inversos es necesario instalar las gramáticas de `tree-sitter`:

.. code-block:: bash

   pip install tree-sitter-languages

Este paquete incluye gramáticas para los lenguajes listados (``python``, ``javascript`` y ``java``) y puede instalarse junto con las dependencias del proyecto.
