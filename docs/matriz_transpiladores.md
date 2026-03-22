# Matriz de transpiladores

Generado desde `scripts/generar_matriz_transpiladores.py`.

## Resumen de política

- **Targets oficiales de transpilación**: `python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java`, `asm`.
- **Targets con runtime oficial verificable**: `python`, `rust`, `javascript`, `cpp`.
- **Targets con verificación ejecutable explícita en CLI**: `python`, `rust`, `javascript`, `cpp`.
- **Targets con soporte oficial mantenido de `corelibs`/`standard_library` en runtime**: `python`, `rust`, `javascript`, `cpp`.
- **Targets con adaptador Holobit mantenido por el proyecto**: `python`, `rust`, `javascript`, `cpp`.
- **Compatibilidad SDK completa**: `python`.
- **Targets sin runtime oficial público aunque tengan generación de código**: `wasm`, `go`, `java`, `asm`.
- **Targets con runtime best-effort no público**: `go`, `java`.
- **Targets solo de transpilación**: `wasm`, `asm`.

## Estado público por backend

| Backend | Nombre | Tier | runtime_publico | holobit_publico | sdk_real |
|---|---|---|---|---|---|
| `python` | Python | Tier 1 | runtime_oficial | sdk_full | full |
| `rust` | Rust | Tier 1 | runtime_oficial | adaptador_mantenido_partial | partial |
| `javascript` | JavaScript | Tier 1 | runtime_oficial | adaptador_mantenido_partial | partial |
| `wasm` | WebAssembly | Tier 1 | solo_transpilacion | partial | partial |
| `go` | Go | Tier 2 | runtime_best_effort_no_publico | partial | partial |
| `cpp` | cpp | Tier 2 | runtime_oficial | adaptador_mantenido_partial | partial |
| `java` | Java | Tier 2 | runtime_best_effort_no_publico | partial | partial |
| `asm` | asm | Tier 2 | solo_transpilacion | partial | partial |

## Matriz contractual

| Backend | Nombre | Tier | runtime_policy | holobit | proyectar | transformar | graficar | corelibs | standard_library |
|---|---|---|---|---|---|---|---|---|---|
| `python` | Python | Tier 1 | runtime_oficial | full | full | full | full | full | full |
| `rust` | Rust | Tier 1 | runtime_oficial | partial | partial | partial | partial | partial | partial |
| `javascript` | JavaScript | Tier 1 | runtime_oficial | partial | partial | partial | partial | partial | partial |
| `wasm` | WebAssembly | Tier 1 | solo_transpilacion | partial | partial | partial | partial | partial | partial |
| `go` | Go | Tier 2 | runtime_best_effort_no_publico | partial | partial | partial | partial | partial | partial |
| `cpp` | cpp | Tier 2 | runtime_oficial | partial | partial | partial | partial | partial | partial |
| `java` | Java | Tier 2 | runtime_best_effort_no_publico | partial | partial | partial | partial | partial | partial |
| `asm` | asm | Tier 2 | solo_transpilacion | partial | partial | partial | partial | partial | partial |

> `runtime_policy` distingue explícitamente entre transpilación oficial, runtime oficial y runtime best-effort no público.
> `holobit_publico` resume la promesa pública: `sdk_full` solo aplica a `python`; `adaptador_mantenido_partial` aplica a `rust`, `javascript` y `cpp`; el resto permanece en `partial`.
