Soporte de backends
===================

La documentación pública de pCobra describe una sola familia de salida: **8 backends oficiales** agrupados en Tier 1 y Tier 2.

.. include:: ../_generated/target_policy_summary.rst

Ejemplos de uso generados desde el registro canónico:

.. include:: ../_generated/cli_backend_examples.rst

Política de targets oficial
---------------------------

Los nombres canónicos y la clasificación por tiers de estos backends se derivan de ``src/pcobra/cobra/transpilers/targets.py``. La documentación pública debe usar únicamente ``python``, ``rust``, ``javascript``, ``wasm``, ``go``, ``cpp``, ``java`` y ``asm``.

Esto describe la **salida oficial de transpilación**, no una promesa uniforme de ejecución. La lectura correcta es:

- Runtime oficial verificable: ``python``, ``rust``, ``javascript``, ``cpp``.
- Runtime best-effort no público: ``go``, ``java``.
- Solo transpilación pública: ``wasm``, ``asm``.
- Compatibilidad SDK completa: solo ``python``.
- Estado Holobit público: ``python`` ``full``; el resto de backends oficiales, ``partial`` según la matriz contractual.

Matriz de características
-------------------------

Para un resumen completo de la cobertura contractual por backend, revisa la matriz de transpiladores:

.. include:: ../../docs/matriz_transpiladores.md

Comandos válidos por destino
----------------------------

Listado generado desde ``LANG_CHOICES`` en
``src/pcobra/cobra/cli/commands/compile_cmd.py`` para evitar desalineaciones
entre documentación y CLI:

.. code-block:: bash

   cobra compilar programa.co --backend asm
   cobra compilar programa.co --backend cpp
   cobra compilar programa.co --backend go
   cobra compilar programa.co --backend java
   cobra compilar programa.co --backend javascript
   cobra compilar programa.co --backend python
   cobra compilar programa.co --backend rust
   cobra compilar programa.co --backend wasm
