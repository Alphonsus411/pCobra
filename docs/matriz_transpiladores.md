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
| `cpp` | cpp | Tier 2 | runtime_oficial | partial | partial | partial | partial | partial | partial |
| `java` | Java | Tier 2 | runtime_best_effort_no_publico | partial | partial | partial | partial | partial | partial |
| `asm` | asm | Tier 2 | solo_transpilacion | partial | partial | partial | partial | partial | partial |

> `runtime_policy` distingue explícitamente entre transpilación oficial, runtime oficial y runtime best-effort no público.

## Compatibilidad real de los Tier 1 parciales

- `javascript`: adaptador oficial con objeto runtime `holobit`, proyecciones 1D/2D/3D/vector, transformaciones base y `graficar` textual; `corelibs`/`standard_library` expuestos mediante alias ejecutables.
- `rust`: adaptador oficial inline con `CobraHolobit`, `CobraRuntimeError`, `Result`, proyecciones y transformaciones base; `corelibs`/`standard_library` materializados como funciones del runtime generado.
- `wasm`: wrappers WAT e imports `pcobra:*` para Holobit, `corelibs` y `standard_library`; soporte real dependiente de host, por eso sigue en `partial`.
