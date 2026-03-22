Soporte de backends
===================

Cobra permite generar código para los destinos definidos por el registro canónico de transpiladores.

.. include:: ../_generated/target_policy_summary.rst

Ejemplos de uso generados desde el registro canónico:

.. include:: ../_generated/cli_backend_examples.rst

Para ``wasm``, el backend genera formato WAT que puede convertirse con
``wat2wasm`` para obtener un módulo binario ejecutable.

Política de targets oficial
---------------------------

Los nombres canónicos y la clasificación por tiers de estos backends se derivan
de ``src/pcobra/cobra/transpilers/targets.py``. La documentación pública debe
usar únicamente ``python``, ``rust``, ``javascript``, ``wasm``, ``go``, ``cpp``,
``java`` y ``asm``.

Esto describe la **salida oficial de transpilación**, no la cobertura de
ejecución. El runtime oficial público de CLI/contenedores está limitado a
``python``, ``javascript``, ``cpp`` y ``rust``. Los targets ``go``, ``java``,
``wasm`` y ``asm`` siguen siendo oficiales para generación de código, pero no
deben presentarse como equivalentes a esos runtimes oficiales ni como soporte
oficial de librerías en ejecución.

Matriz de características
-------------------------

Para un resumen completo de la cobertura por lenguaje, revisa la `matriz de transpiladores <../../docs/matriz_transpiladores.md>`_:

.. include:: ../../docs/matriz_transpiladores.md

Diferencias identificadas
-------------------------

- Go y Java no soportan condicionales ni bucles. Consulta el `issue #11 <../issues/11_soporte_condicionales_bucles_go_java.md>`_ para seguimiento y contribuciones.

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
