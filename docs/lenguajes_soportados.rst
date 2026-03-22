Estado de los lenguajes soportados
=================================

Esta guía separa explícitamente los **targets oficiales de transpilación**, los
**targets con runtime oficial** y los **orígenes de transpilación inversa** para
evitar ambigüedades entre categorías distintas.

Resumen normativo:

- **Targets oficiales de transpilación**: ``python``, ``rust``, ``javascript``, ``wasm``, ``go``, ``cpp``, ``java`` y ``asm``.
- **Targets con runtime oficial verificable**: ``python``, ``rust``, ``javascript`` y ``cpp``.
- **Targets con verificación ejecutable explícita en CLI**: ``python``, ``rust``, ``javascript`` y ``cpp``.
- **Targets con soporte oficial mantenido de** ``corelibs``/**standard_library**
  **en runtime**: ``python``, ``rust``, ``javascript`` y ``cpp``.
- **Targets con soporte Holobit avanzado mantenido por el proyecto**:
  ``python``, ``rust``, ``javascript`` y ``cpp``.
- **Compatibilidad SDK completa**: ``python``.
- **Targets sin runtime oficial público aunque tengan codegen oficial**:
  ``go``, ``java``, ``wasm`` y ``asm``.

La lista canónica completa de targets oficiales de transpilación es:
``python``, ``rust``, ``javascript``, ``wasm``, ``go``, ``cpp``, ``java`` y
``asm``.

Fuentes normativas visibles:

- ``src/pcobra/cobra/transpilers/targets.py`` para la lista canónica y los tiers.
- ``src/pcobra/cobra/cli/target_policies.py`` para la separación entre
  transpilación, runtime oficial y verificación ejecutable.

Tier 1 (soporte principal)
--------------------------

.. list-table:: Backends Tier 1
   :header-rows: 1

   * - Lenguaje
     - Identificador CLI
     - Estado
   * - Python
     - ``python``
     - Estable
   * - JavaScript
     - ``javascript``
     - Estable
   * - Rust
     - ``rust``
     - Estable
   * - WebAssembly (WAT)
     - ``wasm``
     - Estable

Tier 2 (soporte oficial con cobertura parcial)
-------------------------------------

.. list-table:: Backends Tier 2
   :header-rows: 1

   * - Lenguaje
     - Identificador CLI
     - Estado
   * - Go
     - ``go``
     - Parcial
   * - Java
     - ``java``
     - Parcial
   * - ``cpp``
     - ``cpp``
     - Parcial
   * - ``asm``
     - ``asm``
     - Cobertura básica

Targets con runtime oficial
---------------------------

.. list-table:: Targets con runtime oficial
   :header-rows: 1

   * - Lenguaje
     - Identificador CLI
     - Alcance
   * - Python
     - ``python``
     - Runtime oficial
   * - Rust
     - ``rust``
     - Runtime oficial
   * - JavaScript
     - ``javascript``
     - Runtime oficial
   * - ``cpp``
     - ``cpp``
     - Runtime oficial

Capacidades públicas por nivel de promesa
-----------------------------------------

.. list-table:: Diferencia entre codegen, runtime, librerías y SDK
   :header-rows: 1

   * - Backend
     - Runtime oficial verificable
     - Verificación ejecutable CLI
     - ``corelibs``/``standard_library`` oficiales en runtime
     - Holobit avanzado mantenido
     - Compatibilidad SDK completa
   * - ``python``
     - Sí
     - Sí
     - Sí
     - Sí
     - Sí
   * - ``rust``
     - Sí
     - Sí
     - Sí
     - Sí
     - No (sigue en ``partial``)
   * - ``javascript``
     - Sí
     - Sí
     - Sí
     - Sí
     - No (sigue en ``partial``)
   * - ``cpp``
     - Sí
     - Sí
     - Sí
     - Sí
     - No (sigue en ``partial``)
   * - ``wasm``
     - No
     - No
     - No como runtime oficial; solo wrappers/codegen host-managed
     - No como promesa pública de runtime oficial
     - No
   * - ``go``
     - No (best-effort interno/no público)
     - No
     - No como runtime oficial; solo adaptadores mínimos
     - No como promesa pública de runtime oficial
     - No
   * - ``java``
     - No (best-effort interno/no público)
     - No
     - No como runtime oficial; solo adaptadores mínimos
     - No como promesa pública de runtime oficial
     - No
   * - ``asm``
     - No
     - No
     - No como runtime oficial; solo puntos de llamada/diagnóstico
     - No como promesa pública de runtime oficial
     - No


Política de targets oficial
----------------------------

Los targets oficiales de salida tienen una única fuente de verdad en
``src/pcobra/cobra/transpilers/targets.py`` mediante las constantes
``TIER1_TARGETS``, ``TIER2_TARGETS`` y ``OFFICIAL_TARGETS``. La separación
operativa entre targets oficiales de transpilación, targets con runtime
oficial y targets solo de transpilación se refleja en
``src/pcobra/cobra/cli/target_policies.py``. Toda la documentación pública
debe usar únicamente los nombres canónicos ``python``, ``rust``,
``javascript``, ``wasm``, ``go``, ``cpp``, ``java`` y ``asm``.

Reglas del proyecto:

- La CLI pública debe construir sus opciones desde ``OFFICIAL_TARGETS`` y el
  registro canónico de transpiladores, sin listas hardcodeadas duplicadas.
- Los scripts de benchmark y validación CI deben importar utilidades comunes
  basadas en esa misma política, en lugar de redefinir targets por separado.
- Los aliases legacy o targets retirados no deben aparecer en snippets de CLI,
  tablas ni texto narrativo de la documentación pública.
- No deben existir módulos ``to_*.py`` fuera de los 8 backends oficiales.

Transpilación inversa (feature independiente)
---------------------------------------------

La transpilación inversa se documenta como una capacidad separada de los
backends de salida. Su objetivo es convertir código fuente de otros lenguajes
a AST de Cobra para migraciones o análisis. Los orígenes soportados en la base
actual son ``python``, ``javascript`` y ``java``; el destino final debe ser uno
de los 8 backends oficiales de salida.

.. code-block:: bash

   cobra transpilar-inverso script.py --origen=python --destino=javascript

Esta funcionalidad es experimental y su cobertura depende del frontend de
entrada. Los valores ``python``, ``javascript`` y ``java`` se listan aquí como
**orígenes reverse de entrada**, no como destinos oficiales adicionales de
salida equivalentes a los backends Tier 1/Tier 2.

Comparativa de características
------------------------------

La cobertura de características por lenguaje se resume en la matriz de transpiladores:

.. include:: matriz_transpiladores.md

La tabla anterior debe leerse junto con esa matriz: que un backend tenga
``partial`` en Holobit o librerías base significa que **puede generar hooks o
adaptadores**, no que tenga automáticamente runtime oficial verificable ni
compatibilidad SDK completa.

Diferencias identificadas
-------------------------

- Go y Java no soportan condicionales ni bucles. Se recomienda implementar estas
  estructuras; véase el `issue #11 <issues/11_soporte_condicionales_bucles_go_java.md>`_.

Material fuera de política y documentación segregada
---------------------------------------------------

Cualquier documentación sobre IR internos, prototipos o pipelines auxiliares debe leerse como material de **pipeline interno** y mantenerse fuera del recorrido público normal. El material sobre LLVM, reverse desde LaTeX o reverse retirado desde WASM debe permanecer en ``docs/experimental/`` con etiqueta visible de experimental/fuera de política, mientras que ``docs/historico/`` queda reservado para material archivado sin vigencia normativa.
