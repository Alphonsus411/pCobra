Estado de los lenguajes soportados
=================================

La narrativa pública de pCobra es única: el proyecto transpila a **3 backends públicos oficiales** (`python`, `javascript`, `rust`). La lista canónica se deriva de ``src/pcobra/cobra/architecture/backend_policy.py`` (``PUBLIC_BACKENDS``).

.. include:: _generated/official_targets_table.rst

Estado público de runtime, Holobit y SDK
----------------------------------------

.. include:: _generated/runtime_capability_matrix.rst

Lectura correcta de la política pública:

- Los backends públicos de salida son únicamente ``python``, ``javascript`` y ``rust``.
- El runtime oficial verificable para la superficie pública cubre esos tres targets.
- Los backends legacy (`go`, `cpp`, `java`, `wasm`, `asm`) quedan en ruta de compatibilidad interna y no forman parte de la operación pública normal.
- La compatibilidad SDK completa solo puede prometerse para ``python``.
- El soporte Holobit debe leerse siempre junto con la matriz contractual pública: ``python`` es ``full``; ``javascript`` y ``rust`` permanecen en ``partial``.

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
