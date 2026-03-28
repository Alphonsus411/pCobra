# Matriz de compatibilidad de librerías por target oficial

Fecha de actualización: **2026-03-28**.

Este documento publica el inventario técnico y el estado de compatibilidad de librerías clave de pCobra por cada uno de los **8 targets permitidos** (`python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java`, `asm`).

## 1) Inventario de librerías/dependencias clave consumidas por pCobra

- **Runtime base**: `corelibs`, `standard_library`, `holobit-sdk` (solo full en Python), `RestrictedPython` para sandbox.
- **Parser/AST**: `lark`, `tree-sitter` (reverse transpilation), lexer/parser propios.
- **Serialización/configuración**: `jsonschema`, `PyYAML`, `tomli`/`tomllib`.
- **Red/IO**: `requests`, `httpx`, `pexpect` (automatización de procesos/terminal).

> Nota de alcance: en targets no Python, la mayor parte de parser/red/serialización se resuelve en el frontend Python o en el host runtime.

## 2) Pruebas de integración definidas por librería y por target

Suite: `tests/integration/transpilers/test_library_compatibility_matrix.py`

Cobertura:

1. Valida que la matriz cubra exactamente los 8 targets oficiales.
2. Valida contrato por área (`runtime`, `parser`, `serializacion`, `red`) en cada target.
3. Cruza compatibilidad de runtime con el piso contractual oficial (`BACKEND_COMPATIBILITY`).
4. Verifica severidad máxima por target para evitar drift del inventario.

## 3) Resultado de ejecución e incompatibilidades (severidad + workaround)

| Target | Runtime | Parser | Serialización | Red | Severidad máxima |
|---|---|---|---|---|---|
| `python` | full | full | full | full | baja |
| `javascript` | partial | partial | partial | partial | media |
| `rust` | partial | partial | partial | partial | alta |
| `wasm` | partial | none | partial | none | alta |
| `go` | partial | none | partial | none | alta |
| `cpp` | partial | none | partial | none | alta |
| `java` | partial | none | partial | none | alta |
| `asm` | partial | none | none | none | critica |

### Incompatibilidades clave registradas

- **WASM**: depende de runtime host-managed para semántica real de runtime/serialización/red.
  - Workaround: implementar imports host `pcobra:*` y ABI de buffers estable.
- **ASM**: backend de inspección/diagnóstico sin red ni serialización oficial.
  - Workaround: usar ASM solo para auditoría de transpilación, no para ejecución con IO real.
- **Go/Java/C++/Rust/JS**: runtime parcial sin paridad total de SDK Python.
  - Workaround: limitarse al subset contractual y mover funcionalidades avanzadas al host.

## 4) Capas de adaptación para mantener API estable

Se centralizó una capa estable en:

- `src/pcobra/cobra/transpilers/library_compatibility.py`

Esta capa define:

- contrato único `LibraryCompatibilityRecord`,
- matriz `LIBRARY_COMPATIBILITY` por target/área,
- helpers de acceso `get_library_compatibility(...)`,
- cálculo de severidad agregada `highest_severity_for_backend(...)`.

## 5) Gates CI anti-regresión

Se añade gate de compatibilidad de librerías en CI:

- `pytest tests/integration/transpilers/test_library_compatibility_matrix.py`
- `python scripts/ci/validate_library_compatibility_matrix.py`

## 6) Publicación de matriz técnica

Este documento es la publicación técnica consumible por ingeniería para seguimiento de compatibilidad de librerías por target.
