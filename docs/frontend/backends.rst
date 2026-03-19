Soporte de backends
===================

Cobra permite generar código para los siguientes destinos mediante el subcomando
``compilar``: ``python``, ``rust``, ``javascript``, ``wasm``, ``go``, ``cpp``, ``java`` y ``asm``.

Ejemplos de uso:

.. code-block:: bash

   cobra compilar programa.co --backend python
   cobra compilar programa.co --backend javascript
   cobra compilar programa.co --backend rust
   cobra compilar programa.co --backend cpp
   cobra compilar programa.co --backend go
   cobra compilar programa.co --backend java
   cobra compilar programa.co --backend asm
   cobra compilar programa.co --backend wasm

Para ``wasm``, el backend genera formato WAT que puede convertirse con
``wat2wasm`` para obtener un módulo binario ejecutable.

Política de targets oficial
---------------------------

Los nombres canónicos y la clasificación por tiers de estos backends se derivan
de ``src/pcobra/cobra/transpilers/targets.py``. La documentación pública debe
usar únicamente ``python``, ``rust``, ``javascript``, ``wasm``, ``go``, ``cpp``,
``java`` y ``asm``.

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
