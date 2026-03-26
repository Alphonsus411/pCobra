# Matriz de transpiladores

Generado desde `scripts/generar_matriz_transpiladores.py`.

## Resumen de política

- **Backends oficiales de salida**: 8 targets canónicos.
- **Targets oficiales de transpilación**: `python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java`, `asm`.
- **Targets con runtime oficial verificable (full SDK solo en python)**: `python`, `rust`, `javascript`, `cpp`.
- **Targets con verificación ejecutable explícita en CLI**: `python`, `rust`, `javascript`, `cpp`.
- **Targets con runtime best-effort**: `go`, `java`.
- **Targets con soporte oficial mantenido de `corelibs`/`standard_library` (partial fuera de python)**: `python`, `rust`, `javascript`, `cpp`.
- **Targets con adaptador Holobit mantenido por el proyecto (partial fuera de python)**: `python`, `rust`, `javascript`, `cpp`.
- **Compatibilidad SDK completa (solo python)**: `python`.
- **Targets solo de transpilación**: `wasm`, `asm`.

## Estado público por backend

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
