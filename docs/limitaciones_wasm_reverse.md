# Limitaciones del transpílador inverso desde WASM

El soporte actual para convertir código WebAssembly a Cobra es **experimental**.
Solo se reconocen funciones que contengan asignaciones simples de constantes a
variables locales mediante instrucciones `i32.const` seguidas de `local.set`.

No se procesan estructuras de control, llamadas a funciones ni otros tipos de
instrucciones. Esta funcionalidad se ampliará en el futuro.
