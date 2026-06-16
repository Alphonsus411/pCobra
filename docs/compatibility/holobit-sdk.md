# Compatibilidad Holobit SDK

> Estado contractual para los **3 backends públicos oficiales** de pCobra: `python`, `javascript` y `rust`.

## 1) Integraciones directas detectadas con Holobit SDK

Fuente única de verdad técnica (código):

- `src/pcobra/cobra/transpilers/compatibility_matrix.py`
  - `SDK_FULL_BACKENDS` / `SDK_PARTIAL_BACKENDS`
  - `OFFICIAL_RUNTIME_BACKENDS`
  - `BACKEND_HOLOBIT_SDK_CAPABILITIES`

### Wrappers / bindings / adapters

- **Python (`full`)**
  - Wrapper directo hacia `pcobra.core.holobits` y dependencia obligatoria de `holobit_sdk` para operaciones avanzadas.
  - Hooks de runtime consumen la fachada `pcobra.corelibs.holobit` (`crear_holobit`, `proyectar`, `transformar`, `graficar`) y no internals de `pcobra.core.holobits`.
- **JavaScript (`partial`)**
  - Adaptador runtime propio del proyecto (`CobraHolobit` implícito JS) con errores explícitos de contrato parcial.
- **Rust (`partial`)**
  - Adaptador runtime con `CobraHolobit` y `Result<_, CobraRuntimeError>`.

Los targets históricos `go`, `cpp`, `java`, `wasm` y `asm` ya no son BackEnd público ni forman parte de esta matriz de compatibilidad de usuario.

### Categorías runtime oficiales

- **Runtime oficial verificable**: `python`, `rust`, `javascript`.
- **SDK full**: solo `python` (el resto permanece en `partial` o capacidades puntuales `none` según feature).

---

## 2) Matriz target × feature × estado

Leyenda: `full` = paridad contractual completa; `partial` = adaptador oficial limitado; `none` = no soportado.

| Target | Tier | Runtime | Serialización | IPC | Módulos nativos | Import hooks | Estado general |
|---|---|---|---|---|---|---|---|
| `python` | tier1 | full | full | full | full | full | ✅ SDK completo |
| `javascript` | tier1 | partial | partial | none | partial | full | ⚠️ Adaptador parcial |
| `rust` | tier1 | partial | partial | none | partial | full | ⚠️ Adaptador parcial |

---

## 3) Tests mínimos de compatibilidad por target

### Smoke (targets públicos oficiales)

- Generación de código con primitivas Holobit (`holobit`, `proyectar`, `transformar`, `graficar`).
- Verificación de inyección de hooks `cobra_*`.
- Verificación de imports/runtime mínimos por backend.

### Casos críticos

- `runtime`:
  - Python debe permanecer `full`.
  - JavaScript y Rust deben mantenerse al menos en `partial`.
- `import_hooks`:
  - Todos los targets públicos deben permanecer en `full`.
- Cualquier regresión por debajo del mínimo contractual en esos puntos bloquea release.

---

## 4) Limitaciones explícitas y fallback oficial

- **Python:** sin `holobit_sdk`, fallo explícito (`ModuleNotFoundError`), sin fallback silencioso.
- **JavaScript/Rust:** contrato `partial`, con adaptador oficial y errores explícitos cuando la operación no está soportada.

---

## 5) Política de release (gate)

Toda documentación pública, configuración de targets y selector de backend debe listar exclusivamente `python`, `javascript` y `rust`.
