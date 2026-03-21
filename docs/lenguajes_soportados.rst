Estado de los lenguajes soportados
=================================

Esta guía separa explícitamente los **targets oficiales de transpilación**, los
**targets con runtime oficial** y los **orígenes de transpilación inversa** para
evitar ambigüedades entre categorías distintas.

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

Tier 2 (soporte parcial/experimental)
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
entrada, por lo que no debe interpretarse como soporte de salida equivalente a
los backends Tier 1/Tier 2.

Comparativa de características
------------------------------

La cobertura de características por lenguaje se resume en la matriz de transpiladores:

.. include:: matriz_transpiladores.md

Diferencias identificadas
-------------------------

- Go y Java no soportan condicionales ni bucles. Se recomienda implementar estas
  estructuras; véase el `issue #11 <issues/11_soporte_condicionales_bucles_go_java.md>`_.
