# Matriz de transpiladores

> ⚠️ Documento parcialmente derivado: los bloques marcados como `BEGIN/END GENERATED`
> se regeneran automáticamente y no deben editarse manualmente.

Fuente de generación: `scripts/generar_matriz_transpiladores.py`.

## Resumen de política

<!-- BEGIN GENERATED MATRIZ POLICY SUMMARY -->
- **Backends oficiales de salida**: 8 targets canónicos.
- **Targets oficiales de transpilación**: `python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java`, `asm`.
- **Targets con runtime oficial verificable (full SDK solo en python)**: `python`, `rust`, `javascript`, `cpp`.
- **Targets con verificación ejecutable explícita en CLI**: `python`, `rust`, `javascript`, `cpp`.
- **Targets con runtime best-effort**: `go`, `java`.
- **Targets con soporte oficial mantenido de `corelibs`/`standard_library` (partial fuera de python)**: `python`, `rust`, `javascript`, `cpp`.
- **Targets con adaptador Holobit mantenido por el proyecto (partial fuera de python)**: `python`, `rust`, `javascript`, `cpp`.
- **Compatibilidad SDK completa (solo python)**: `python`.
- **Targets solo de transpilación**: `wasm`, `asm`.
<!-- END GENERATED MATRIZ POLICY SUMMARY -->

## Estado público por backend

<!-- BEGIN GENERATED MATRIZ STATUS TABLE -->
| Backend | Nombre | Tier | runtime_publico | holobit_publico | sdk_real |
|---|---|---|---|---|---|
| `python` | Python | Tier 1 | runtime oficial | SDK full solo python | full |
| `rust` | Rust | Tier 1 | runtime oficial | adaptador mantenido (partial) | partial |
| `javascript` | JavaScript | Tier 1 | runtime oficial | adaptador mantenido (partial) | partial |
| `wasm` | WebAssembly | Tier 1 | solo transpilación | partial | partial |
| `go` | Go | Tier 2 | best-effort | partial | partial |
| `cpp` | cpp | Tier 2 | runtime oficial | adaptador mantenido (partial) | partial |
| `java` | Java | Tier 2 | best-effort | partial | partial |
| `asm` | asm | Tier 2 | solo transpilación | partial | partial |
<!-- END GENERATED MATRIZ STATUS TABLE -->

## Matriz contractual

| Backend | Nombre | Tier | runtime_policy | holobit | proyectar | transformar | graficar | corelibs | standard_library |
|---|---|---|---|---|---|---|---|---|---|
| `python` | Python | Tier 1 | runtime oficial | full | full | full | full | full | full |
| `rust` | Rust | Tier 1 | runtime oficial | partial | partial | partial | partial | partial | partial |
| `javascript` | JavaScript | Tier 1 | runtime oficial | partial | partial | partial | partial | partial | partial |
| `wasm` | WebAssembly | Tier 1 | solo transpilación | partial | partial | partial | partial | partial | partial |
| `go` | Go | Tier 2 | best-effort | partial | partial | partial | partial | partial | partial |
| `cpp` | cpp | Tier 2 | runtime oficial | partial | partial | partial | partial | partial | partial |
| `java` | Java | Tier 2 | best-effort | partial | partial | partial | partial | partial | partial |
| `asm` | asm | Tier 2 | solo transpilación | partial | partial | partial | partial | partial | partial |

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
| `rust` | `holobit` | `partial` | `let hb = cobra_holobit(vec![1, 2, 3]);` |
| `rust` | `proyectar` | `partial` | `CobraRuntimeError::new(format!("Runtime Holobit Rust: feature={}; contrato partial; backend sin holobit_sdk; {}. {}", feature, detail.into(), COBRA_HOLOBIT_PARTIAL_CONTRACT_NOTE))` |
| `rust` | `transformar` | `partial` | `CobraRuntimeError::new(format!("Runtime Holobit Rust: feature={}; contrato partial; backend sin holobit_sdk; {}. {}", feature, detail.into(), COBRA_HOLOBIT_PARTIAL_CONTRACT_NOTE))` |
| `rust` | `graficar` | `partial` | `CobraRuntimeError::new(format!("Runtime Holobit Rust: feature={}; contrato partial; backend sin holobit_sdk; {}. {}", feature, detail.into(), COBRA_HOLOBIT_PARTIAL_CONTRACT_NOTE))` |
| `rust` | `corelibs` | `partial` | `longitud("cobra");` |
| `rust` | `standard_library` | `partial` | `mostrar("hola");` |
| `javascript` | `holobit` | `partial` | `let hb = cobra_holobit([1, 2, 3]);` |
| `javascript` | `proyectar` | `partial` | `throw new Error(`Runtime Holobit JavaScript: feature=${feature}; contrato partial; backend sin holobit_sdk; ${detail}. ${COBRA_HOLOBIT_PARTIAL_CONTRACT_NOTE}`);` |
| `javascript` | `transformar` | `partial` | `throw new Error(`Runtime Holobit JavaScript: feature=${feature}; contrato partial; backend sin holobit_sdk; ${detail}. ${COBRA_HOLOBIT_PARTIAL_CONTRACT_NOTE}`);` |
| `javascript` | `graficar` | `partial` | `throw new Error(`Runtime Holobit JavaScript: feature=${feature}; contrato partial; backend sin holobit_sdk; ${detail}. ${COBRA_HOLOBIT_PARTIAL_CONTRACT_NOTE}`);` |
| `javascript` | `corelibs` | `partial` | `longitud('cobra');` |
| `javascript` | `standard_library` | `partial` | `mostrar('hola');` |
| `wasm` | `holobit` | `partial` | `(drop (call $cobra_holobit (i32.const 1)))` |
| `wasm` | `proyectar` | `partial` | `;; backend wasm: contrato partial; no usa holobit_sdk dentro del módulo generado y depende del host para la semántica completa` |
| `wasm` | `transformar` | `partial` | `;; backend wasm: contrato partial; no usa holobit_sdk dentro del módulo generado y depende del host para la semántica completa` |
| `wasm` | `graficar` | `partial` | `;; backend wasm: contrato partial; no usa holobit_sdk dentro del módulo generado y depende del host para la semántica completa` |
| `wasm` | `corelibs` | `partial` | `(import "pcobra:corelibs" "longitud" (func $host_longitud (param i32) (result i32)))` |
| `wasm` | `standard_library` | `partial` | `(import "pcobra:standard_library" "mostrar" (func $host_mostrar (param i32)))` |
| `go` | `holobit` | `partial` | `hb := cobra_holobit([]float64{1, 2, 3})` |
| `go` | `proyectar` | `partial` | `panic(fmt.Sprintf("Runtime Holobit Go: feature=%s; contrato partial; backend sin holobit_sdk; %s. %s", feature, detail, cobraHolobitPartialContractNote))` |
| `go` | `transformar` | `partial` | `panic(fmt.Sprintf("Runtime Holobit Go: feature=%s; contrato partial; backend sin holobit_sdk; %s. %s", feature, detail, cobraHolobitPartialContractNote))` |
| `go` | `graficar` | `partial` | `panic(fmt.Sprintf("Runtime Holobit Go: feature=%s; contrato partial; backend sin holobit_sdk; %s. %s", feature, detail, cobraHolobitPartialContractNote))` |
| `go` | `corelibs` | `partial` | `longitud("cobra")` |
| `go` | `standard_library` | `partial` | `mostrar("hola")` |
| `cpp` | `holobit` | `partial` | `auto hb = cobra_holobit({ 1, 2, 3 });` |
| `cpp` | `proyectar` | `partial` | `return std::runtime_error("Runtime Holobit C++: feature=" + feature + "; contrato partial; backend sin holobit_sdk; " + detail + ". " + COBRA_HOLOBIT_PARTIAL_CONTRACT_NOTE);` |
| `cpp` | `transformar` | `partial` | `return std::runtime_error("Runtime Holobit C++: feature=" + feature + "; contrato partial; backend sin holobit_sdk; " + detail + ". " + COBRA_HOLOBIT_PARTIAL_CONTRACT_NOTE);` |
| `cpp` | `graficar` | `partial` | `return std::runtime_error("Runtime Holobit C++: feature=" + feature + "; contrato partial; backend sin holobit_sdk; " + detail + ". " + COBRA_HOLOBIT_PARTIAL_CONTRACT_NOTE);` |
| `cpp` | `corelibs` | `partial` | `longitud("cobra");` |
| `cpp` | `standard_library` | `partial` | `mostrar("hola");` |
| `java` | `holobit` | `partial` | `Object hb = cobra_holobit(new double[]{1, 2, 3});` |
| `java` | `proyectar` | `partial` | `return new UnsupportedOperationException("Runtime Holobit Java: feature=" + feature + "; contrato partial; backend sin holobit_sdk; " + detail + ". " + COBRA_HOLOBIT_PARTIAL_CONTRACT_NOTE);` |
| `java` | `transformar` | `partial` | `return new UnsupportedOperationException("Runtime Holobit Java: feature=" + feature + "; contrato partial; backend sin holobit_sdk; " + detail + ". " + COBRA_HOLOBIT_PARTIAL_CONTRACT_NOTE);` |
| `java` | `graficar` | `partial` | `return new UnsupportedOperationException("Runtime Holobit Java: feature=" + feature + "; contrato partial; backend sin holobit_sdk; " + detail + ". " + COBRA_HOLOBIT_PARTIAL_CONTRACT_NOTE);` |
| `java` | `corelibs` | `partial` | `longitud("cobra");` |
| `java` | `standard_library` | `partial` | `mostrar("hola");` |
| `asm` | `holobit` | `partial` | `HOLOBIT hb [1, 2, 3]` |
| `asm` | `proyectar` | `partial` | `TRAP` |
| `asm` | `transformar` | `partial` | `TRAP` |
| `asm` | `graficar` | `partial` | `TRAP` |
| `asm` | `corelibs` | `partial` | `CALL longitud 'cobra'` |
| `asm` | `standard_library` | `partial` | `CALL mostrar 'hola'` |
