# EXPERIMENTAL · FUERA DE POLÍTICA · Plan archivado de Hololang

> **Estado:** material conservado por contexto histórico/técnico.
>
> **Política:** este documento **no forma parte del plan vigente** y **no amplía `OFFICIAL_TARGETS`**. `hololang` no debe interpretarse aquí como target público de `cobra compilar`, sino como pipeline/IR interno o línea de investigación experimental.
>
> **Separación visible:** cualquier enlace a este archivo desde documentación activa debe etiquetarse como **experimental** o **fuera de política**.

## Motivo del archivado

La propuesta original de nuevas funcionalidades mezclaba mejoras vigentes de biblioteca estándar y asincronía con una línea de investigación sobre computación cuántica holográfica apoyada en Hololang. Esa mezcla ya no refleja el plan vigente del repositorio, por lo que el bloque se conserva aquí únicamente como contexto.

## Resumen del bloque archivado

- Se exploraba un puente `Cobra ↔ Hololang` para algoritmos cuánticos de alto nivel.
- Se contemplaban decoradores como `@cuantico`, primitivas `holo.cuantica` y un simulador local.
- El objetivo era producir IR/pipeline interno relacionado con Hololang, no exponer un target público adicional.

## Alcance técnico reescrito con la estructura actual

Si esta línea de investigación se retomara en el futuro, debería describirse con la estructura actual del repositorio:

- `src/pcobra/cobra/experimental/hololang/`: parser y reverse experimental de Hololang.
- `src/pcobra/cobra/transpilers/hololang_bridge.py`: puente interno entre estructuras Hololang IR y AST Cobra.
- `src/pcobra/cobra/transpilers/transpiler/`: backends oficiales de salida; **no** debe ampliarse con `hololang` sin cambiar la política pública.

## Componentes que quedaron archivados

### EXPERIMENTAL · Decorador `@cuantico`
- Idea original: marcar funciones Cobra para enviarlas a una representación cuántica/holográfica.
- Estado actual: sin plan vigente de implementación.
- Restricción de política: no presentarlo como feature pública comprometida ni como target nuevo.

### EXPERIMENTAL · Módulo `holo.cuantica`
Primitivas exploradas:
- `prepara_estado(base, amplitudes)`
- `aplica_puerta(nombre, qubits, parametros=None)`
- `mide(qubits, repeticion=1)`
- `superposicion(qubits)`

### EXPERIMENTAL · Pipeline interno Hololang
Flujo propuesto en la versión archivada:
1. El usuario declaraba `@cuantico` y usaba primitivas `holo.cuantica`.
2. Cobra transformaba el AST hacia nodos o IR internos.
3. El pipeline Hololang generaba una representación intermedia holográfica para simulación o hardware.
4. Los resultados volvían a Cobra para su post-procesamiento.

**Nota de política:** incluso en este escenario experimental, Hololang seguiría siendo un pipeline interno y no un destino público equivalente a `python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java` o `asm`.

## Tareas archivadas de la propuesta original

### EXPERIMENTAL · F3.1 – Especificación del decorador `@cuantico`
- Definir sintaxis, opciones y metadatos.
- Documentación hipotética: RFC experimental, no normativa.

### EXPERIMENTAL · F3.2 – Integración con Hololang IR
- Traducir estructuras Cobra hacia un pipeline Hololang interno.
- Rutas actuales orientativas: `src/pcobra/cobra/experimental/hololang/` y `src/pcobra/cobra/transpilers/hololang_bridge.py`.
- **No** añadir `hololang` a `OFFICIAL_TARGETS`.

### EXPERIMENTAL · F3.3 – Simulador y adaptadores
- Explorar simulador local y conectores a hardware externo.
- Estado: investigación archivada.

### EXPERIMENTAL · F3.4 – Seguridad y auditoría
- Lista blanca de puertas, límites de recursos y bitácoras.
- Estado: investigación archivada.

## Nota final de conservación

Este archivo se mantiene para preservar contexto técnico e histórico. Cualquier reactivación futura debería abrirse como propuesta nueva, separada del plan activo y acompañada de una revisión explícita de la política de targets.
