Estado de los lenguajes soportados
=================================

Esta guía separa los destinos de transpilación por nivel de soporte para evitar
ambigüedades entre backends principales y experimentales.

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
   * - C++
     - ``cpp``
     - Parcial
   * - Ensamblador
     - ``asm``
     - Cobertura básica


Regla de fuente única para targets oficiales
-------------------------------------------

Los targets oficiales de salida tienen una única fuente de verdad en
``src/pcobra/cobra/transpilers/targets.py`` mediante las constantes
``TIER1_TARGETS``, ``TIER2_TARGETS`` y ``OFFICIAL_TARGETS``.

Reglas del proyecto:

- La CLI pública debe construir sus opciones desde ``OFFICIAL_TARGETS`` y el
  registro canónico de transpiladores, sin listas hardcodeadas duplicadas.
- Los scripts de benchmark y validación CI deben importar utilidades comunes
  basadas en esa misma política, en lugar de redefinir targets por separado.
- No deben existir módulos ``to_*.py`` fuera de los 8 backends oficiales.

Transpilación inversa (feature independiente)
---------------------------------------------

La transpilación inversa se documenta como una capacidad separada de los
backends de salida. Su objetivo es convertir código fuente de otros lenguajes
a AST de Cobra para migraciones o análisis.

.. code-block:: bash

   cobra transpilar-inverso script.py --origen=python --destino=cobra

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
