# [RETIRADO/EXPERIMENTAL] Limitaciones del reverse desde WASM

> **Estado:** retirado de la política pública vigente.
> **Ámbito:** referencia histórica/experimental de un origen reverse no oficial.
> **Política:** la documentación principal no debe presentar WASM como origen reverse soportado.

El soporte que existió para convertir código WebAssembly a Cobra era **experimental**.
Solo se reconocían funciones que contuvieran asignaciones simples de constantes a variables locales mediante instrucciones `i32.const` seguidas de `local.set`.

No se procesaban estructuras de control, llamadas a funciones ni otros tipos de instrucciones. Esta referencia se conserva solo para contexto histórico y no describe una capacidad mantenida por la política actual.
