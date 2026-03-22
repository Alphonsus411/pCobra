# Matriz de transpiladores

Generado desde `scripts/generar_matriz_transpiladores.py`.

## Resumen de política

- **Targets oficiales de transpilación**: `python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java`, `asm`.
- **Targets con runtime oficial**: `python`, `rust`, `javascript`, `cpp`.
- **Targets con runtime best-effort no público**: `go`, `java`.
- **Targets solo de transpilación**: `wasm`, `asm`.

## Matriz contractual

| Backend | Nombre | Tier | runtime_policy | holobit | proyectar | transformar | graficar | corelibs | standard_library |
|---|---|---|---|---|---|---|---|---|---|
| `python` | Python | Tier 1 | runtime_oficial | full | full | full | full | full | full |
| `rust` | Rust | Tier 1 | runtime_oficial | partial | partial | partial | partial | partial | partial |
| `javascript` | JavaScript | Tier 1 | runtime_oficial | partial | partial | partial | partial | partial | partial |
| `wasm` | WebAssembly | Tier 1 | solo_transpilacion | partial | partial | partial | partial | partial | partial |
| `go` | Go | Tier 2 | runtime_best_effort_no_publico | partial | partial | partial | partial | partial | partial |
| `cpp` | C++ | Tier 2 | runtime_oficial | partial | partial | partial | partial | partial | partial |
| `java` | Java | Tier 2 | runtime_best_effort_no_publico | partial | partial | partial | partial | partial | partial |
| `asm` | Ensamblador | Tier 2 | solo_transpilacion | partial | partial | partial | partial | partial | partial |

> `runtime_policy` distingue explícitamente entre transpilación oficial, runtime oficial y runtime best-effort no público.
