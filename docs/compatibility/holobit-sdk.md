# Compatibilidad Holobit SDK (v2026-03-28)

> Estado contractual versionado para los 8 targets oficiales de pcobra.

## 1) Integraciones directas detectadas con Holobit SDK

Fuente única de verdad técnica (código):

- `src/pcobra/cobra/transpilers/compatibility_matrix.py`
  - `SDK_FULL_BACKENDS` / `SDK_PARTIAL_BACKENDS`
  - `OFFICIAL_RUNTIME_BACKENDS` / `BEST_EFFORT_RUNTIME_BACKENDS` / `TRANSPILATION_ONLY_BACKENDS`
  - `BACKEND_HOLOBIT_SDK_CAPABILITIES`

### Wrappers / bindings / adapters

- **Python (`full`)**
  - Wrapper directo hacia `pcobra.core.holobits` y dependencia obligatoria de `holobit_sdk` para operaciones avanzadas.
  - Hooks de runtime: `cobra_holobit`, `cobra_proyectar`, `cobra_transformar`, `cobra_graficar`.
- **JavaScript (`partial`)**
  - Adaptador runtime propio del proyecto (`CobraHolobit` implícito JS) con errores explícitos de contrato parcial.
- **Rust (`partial`)**
  - Adaptador runtime con `CobraHolobit` y `Result<_, CobraRuntimeError>`.
- **WASM (`partial`)**
  - Binding host-managed por imports `pcobra:holobit` (puente contractual, no semántica completa local).
- **Go / C++ / Java (`partial`)**
  - Adaptadores runtime best-effort (Go/Java) y mantenido oficialmente (C++), con errores explícitos sin fallback silencioso.
- **ASM (`partial`)**
  - Capa de inspección/diagnóstico: hooks simbólicos y `TRAP` para capacidades no resueltas por runtime externo.

### Import hooks

Todos los targets oficiales mantienen hooks canónicos `cobra_*` para Holobit. Esta capacidad es **crítica** para Tier 1 y se bloquea release si baja del mínimo.

### Categorías runtime oficiales (sin inflar compatibilidad)

- **Runtime oficial verificable**: `python`, `rust`, `javascript`, `cpp`.
- **Runtime best-effort no público**: `go`, `java`.
- **Solo transpilación**: `wasm`, `asm`.
- **SDK full**: solo `python` (el resto permanece en `partial` o capacidades puntuales `none` según feature).

---

## 2) Matriz target × feature × estado

Leyenda: `full` = paridad contractual completa; `partial` = adaptador oficial limitado; `none` = no soportado.

| Target | Tier | Runtime | Serialización | IPC | Módulos nativos | Import hooks | Estado general |
|---|---|---|---|---|---|---|---|
| `python` | tier1 | full | full | full | full | full | ✅ SDK completo |
| `javascript` | tier1 | partial | partial | none | partial | full | ⚠️ Adaptador parcial |
| `rust` | tier1 | partial | partial | none | partial | full | ⚠️ Adaptador parcial |
| `wasm` | tier1 | partial | partial | partial | none | full | ⚠️ Host-managed parcial |
| `go` | tier2 | partial | partial | none | partial | full | ⚠️ Best-effort |
| `cpp` | tier2 | partial | partial | none | partial | full | ⚠️ Runtime parcial mantenido |
| `java` | tier2 | partial | partial | none | partial | full | ⚠️ Best-effort |
| `asm` | tier2 | partial | none | none | none | full | ⚠️ Inspección/diagnóstico |

---

## 3) Tests mínimos de compatibilidad por target

### Smoke (todos los targets oficiales)

- Generación de código con primitivas Holobit (`holobit`, `proyectar`, `transformar`, `graficar`).
- Verificación de inyección de hooks `cobra_*`.
- Verificación de imports/runtime mínimos por backend.

### Casos críticos (Tier 1)

- `runtime`:
  - Python debe permanecer `full`.
  - JavaScript, Rust y WASM deben mantenerse al menos en `partial`.
- `import_hooks`:
  - Todos los Tier 1 deben permanecer en `full`.
- Cualquier regresión por debajo del mínimo contractual en esos puntos bloquea release.

---

## 4) Limitaciones explícitas y fallback oficial

- **Python:** sin `holobit_sdk`, fallo explícito (`ModuleNotFoundError`), sin fallback silencioso.
- **JavaScript/Rust/Go/C++/Java:** contrato `partial`, con adaptador oficial y errores explícitos cuando la operación no está soportada.
- **WASM:** semántica final dependiente del host (`pcobra:holobit`, `pcobra:corelibs`, `pcobra:standard_library`).
- **ASM:** no ejecuta semántica avanzada local; requiere runtime externo y señala `TRAP`.

---

## 5) Política de release (gate)

El release se debe bloquear si un target Tier 1 rompe cualquier capacidad crítica Holobit:

- `runtime`
- `import_hooks`

Este gate se valida automáticamente por CI a partir de la matriz `BACKEND_HOLOBIT_SDK_CAPABILITIES` y el piso `MIN_REQUIRED_TIER1_HOLOBIT_CAPABILITIES`.
