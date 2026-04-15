# Matriz de transpiladores

> ⚠️ Documento parcialmente derivado: los bloques marcados como `BEGIN/END GENERATED`
> son **obligatorios**, se regeneran automáticamente y no deben editarse manualmente.

Fuente de generación: `scripts/generar_matriz_transpiladores.py`.

## Resumen de política

<!-- BEGIN GENERATED MATRIZ POLICY SUMMARY -->
- **Backends oficiales de salida**: 3 targets canónicos.
- **Targets oficiales de transpilación**: `python`, `javascript`, `rust`.
- **Targets con runtime oficial verificable (full SDK solo en python)**: `python`, `javascript`, `rust`.
- **Targets con verificación ejecutable explícita en CLI**: `python`, `javascript`, `rust`.
- **Targets con runtime best-effort**: .
- **Targets con soporte oficial mantenido de `corelibs`/`standard_library` (partial fuera de python)**: `python`, `javascript`, `rust`.
- **Targets con adaptador Holobit mantenido por el proyecto (partial fuera de python)**: `python`, `javascript`, `rust`.
- **Compatibilidad SDK completa (solo python)**: `python`.
- **Targets solo de transpilación**: .
- **Targets legacy/internal (no públicos)**: go, cpp, java, wasm, asm.
<!-- END GENERATED MATRIZ POLICY SUMMARY -->

## Estado público por backend

<!-- BEGIN GENERATED MATRIZ STATUS TABLE -->
| Backend | Nombre | Tier | runtime_publico | holobit_publico | sdk_real |
|---|---|---|---|---|---|
| `python` | Python | Tier 1 | runtime oficial | SDK full solo python | full |
| `javascript` | JavaScript | Tier 1 | runtime oficial | adaptador mantenido (partial) | partial |
| `rust` | Rust | Tier 1 | runtime oficial | adaptador mantenido (partial) | partial |
<!-- END GENERATED MATRIZ STATUS TABLE -->

## Matriz contractual

| Backend | Nombre | Tier | runtime_policy | holobit | proyectar | transformar | graficar | corelibs | standard_library |
|---|---|---|---|---|---|---|---|---|---|
| `python` | Python | Tier 1 | runtime oficial | full | full | full | full | full | full |
| `javascript` | JavaScript | Tier 1 | runtime oficial | partial | partial | partial | partial | partial | partial |
| `rust` | Rust | Tier 1 | runtime oficial | partial | partial | partial | partial | full | full |

> `runtime_policy` distingue explícitamente entre runtime oficial, best-effort y solo transpilación.
> `holobit_publico` resume la promesa pública: `SDK full solo python` aplica únicamente a `python`; `rust`, `javascript` y `cpp` se publican como `adaptador mantenido (partial)`; el resto permanece en `partial`.

## Evidencia técnica automática (derivada de goldens)

| Backend | Feature | Nivel contrato | Evidencia automática |
|---|---|---|---|
| `python` | `holobit` | `full` | `hb = cobra_holobit([1, 2, 3])` |
| `python` | `proyectar` | `full` | `cobra_proyectar(hb, '2d')` |
| `python` | `transformar` | `full` | `cobra_transformar(hb, 'rotar', 90)` |
| `python` | `graficar` | `full` | `def cobra_graficar(hb):` |
| `python` | `corelibs` | `full` | `longitud('cobra')` |
| `python` | `standard_library` | `full` | `mostrar('hola')` |
| `javascript` | `holobit` | `partial` | `let hb = cobra_holobit([1, 2, 3]);` |
| `javascript` | `proyectar` | `partial` | `throw new Error(`Runtime Holobit JavaScript: feature=${feature}; contrato partial; backend sin holobit_sdk; ${detail}. ${COBRA_HOLOBIT_PARTIAL_CONTRACT_NOTE}`);` |
| `javascript` | `transformar` | `partial` | `throw new Error(`Runtime Holobit JavaScript: feature=${feature}; contrato partial; backend sin holobit_sdk; ${detail}. ${COBRA_HOLOBIT_PARTIAL_CONTRACT_NOTE}`);` |
| `javascript` | `graficar` | `partial` | `throw new Error(`Runtime Holobit JavaScript: feature=${feature}; contrato partial; backend sin holobit_sdk; ${detail}. ${COBRA_HOLOBIT_PARTIAL_CONTRACT_NOTE}`);` |
| `javascript` | `corelibs` | `partial` | `longitud('cobra');` |
| `javascript` | `standard_library` | `partial` | `mostrar('hola');` |
| `rust` | `holobit` | `partial` | `let hb = cobra_holobit(vec![1, 2, 3]);` |
| `rust` | `proyectar` | `partial` | `CobraRuntimeError::new(format!("Runtime Holobit Rust: feature={}; contrato partial; backend sin holobit_sdk; {}. {}", feature, detail.into(), COBRA_HOLOBIT_PARTIAL_CONTRACT_NOTE))` |
| `rust` | `transformar` | `partial` | `CobraRuntimeError::new(format!("Runtime Holobit Rust: feature={}; contrato partial; backend sin holobit_sdk; {}. {}", feature, detail.into(), COBRA_HOLOBIT_PARTIAL_CONTRACT_NOTE))` |
| `rust` | `graficar` | `partial` | `CobraRuntimeError::new(format!("Runtime Holobit Rust: feature={}; contrato partial; backend sin holobit_sdk; {}. {}", feature, detail.into(), COBRA_HOLOBIT_PARTIAL_CONTRACT_NOTE))` |
| `rust` | `corelibs` | `full` | `longitud("cobra");` |
| `rust` | `standard_library` | `full` | `mostrar("hola");` |
