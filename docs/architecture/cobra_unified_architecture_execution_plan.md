# Cobra unificado: diseño objetivo y refactor parcial seguro (A–I)

## Contrato unificado (aplica a todo el plan)

- Cobra es el **único lenguaje/interfaz pública**.
- Solo existen **3 backends internos oficiales**: `python`, `javascript`, `rust`.
- La decisión de backend es **interna** (no configurable por usuario final), salvo hints internos controlados.

Este plan aterriza la transición de Cobra como **lenguaje único visible** con tres backends oficiales internos: `python`, `javascript`, `rust`, manteniendo intactos lexer/parser/AST/transpiladores existentes.

---

## A) Architecture overview

- **Frontera pública única**: el usuario solo interactúa con Cobra (`cobra run/build/test/mod`).
- **Resolución interna**: toda ruta pública pasa por `backend_pipeline`.
- **Backends oficiales públicos**: Python, JavaScript y Rust.
- **Compatibilidad legacy**: se conserva solo para migración interna y fuera de UX pública.

Flujo canónico:

`Código Cobra -> Frontend (sin cambios) -> backend_pipeline -> transpilador interno -> binding/runtime`

---

## B) Core module alignment

### Módulos alineados con la arquitectura objetivo

1. `pcobra.cobra.architecture.backend_policy`
   - Define contrato oficial de backends públicos (`python/javascript/rust`) e inventario legacy interno.
2. `pcobra.cobra.build.backend_pipeline`
   - Fachada interna aprobada para resolver backend + runtime y disparar transpilers sin exposición directa.
3. `pcobra.cobra.bindings.runtime_manager`
   - Contrato de seguridad, bridge y ABI por backend oficial.
4. `pcobra.cobra.imports.resolver`
   - Contrato de resolución de imports con precedencia, colisiones e inyección de adapter.
5. `pcobra.cobra.stdlib_contract.*`
   - Fuente declarativa de módulos públicos `cobra.core`, `cobra.datos`, `cobra.web`, `cobra.system`.

### Componentes obsoletos para retirada gradual (sin ruptura inmediata)

- Backends legacy internos:
  - `go`
  - `cpp`
  - `java`
  - `wasm`
  - `asm`
- Comandos legacy de CLI v1/v2-compat que no pertenecen al contrato público.
- Scripts/documentación pública que referencien targets no oficiales.

---

## C) CLI redesign

### UX pública objetivo (estable)

```bash
cobra run archivo.cobra
cobra build archivo.cobra
cobra test archivo.cobra
cobra mod list
```

### Estrategia de simplificación aplicada

- Mantener compatibilidad interna con flags avanzadas.
- Ocultar de la ayuda pública flags que exponen detalles de backend/runtime.
- Consolidar guías y ejemplos de usuario en `run/build/test/mod`.

---

## D) Transpiler integration (hidden)

Reglas de integración:

1. No invocar transpilers directamente desde la UX pública.
2. Resolver backend con orquestador (`backend_pipeline` + `BuildOrchestrator`).
3. Validar bridge + seguridad + ABI con `RuntimeManager`.
4. Invocar transpiler oficial desde el registro interno.

Selección de backend (resumen):

- Entrada: archivo/código + hints internos.
- Resolución: backend canónico de contrato público.
- Ejecución: runtime bridge correspondiente (Python direct import, JS runtime bridge, Rust FFI).

---

## E) Stdlib design

Diseño contractual de módulos:

1. `cobra.core`
   - Base transversal (tipos, utilidades base, contratos comunes).
2. `cobra.datos` (prioridad Python)
   - Operaciones de datos con fallback controlado.
3. `cobra.web` (prioridad JavaScript)
   - Capacidades orientadas a runtime web/js.
4. `cobra.system` (híbrido Rust/Python)
   - Operaciones de sistema con ruta nativa/segura y fallback explícito.

Reglas:

- API de usuario siempre en Cobra.
- Mapeo runtime/backend definido por contrato (`stdlib_contract`).
- Fallbacks auditables y explícitos (no implícitos).

---

## F) Import system

Casos soportados:

1. **Bridge Python**: `importar pandas`
2. **Stdlib Cobra**: `importar datos` / `importar cobra.datos`
3. **Híbridos**: definidos en configuración (`imports.hybrid_modules`)

Orden de resolución contractual:

1. `stdlib`
2. `project`
3. `python_bridge`
4. `hybrid`

Colisiones:

- `warn` (transición),
- `strict_error`,
- `namespace_required` (recomendado para endurecimiento).

Inyección:

- `backend_adapter` + metadata de resolución en módulo cargado para trazabilidad.

---

## G) Binding system

Rutas oficiales:

1. Python → `python_direct_import`
2. JavaScript → `javascript_runtime_bridge`
3. Rust → `rust_compiled_ffi`

Validaciones:

- Seguridad por comando (`run`, `test`, `build`).
- Negociación ABI por backend.
- Consistencia de ruta contractual ↔ bridge seleccionado.

---

## H) Elements to remove (safe backlog)

Eliminar por lotes pequeños y con métricas de uso:

1. Exposición pública de comandos/flags ligados a backends legacy.
2. Referencias en docs públicas a targets fuera de `python/javascript/rust`.
3. Jobs CI/scripts exclusivamente legacy sin consumidores activos.

Condición de retiro:

- Mantener ventanas de transición y guías de migración antes de borrar.

---

## I) Documentation updates

Actualizar progresivamente:

1. `README.md`
   - Enfatizar Cobra como interfaz única.
   - Reafirmar transpilación oculta e interna.
2. `docs/architecture/*`
   - Visión de capas, import contract y binding contract.
3. Guías de CLI
   - Mostrar solo flujo público `run/build/test/mod`.
4. Changelog / notas de release
   - Documentar retiro gradual legacy y fechas objetivo.

---

## Tareas estructuradas para implementar (paso a paso)

### Bloque 1 — Contrato y gobernanza (riesgo bajo)

1. Verificar que `PUBLIC_BACKENDS` sea la única fuente para superficies públicas.
2. Auditar comandos públicos y ocultar detalles de backend en help.
3. Publicar inventario de rutas legacy activas (código, tests y docs).

### Bloque 2 — CLI pública mínima (riesgo bajo)

1. Mantener `run/build/test/mod` como contrato visible.
2. Encapsular flags legacy como internas (sin romper compatibilidad).
3. Actualizar ejemplos de CLI en README y docs frontend.

### Bloque 3 — Imports/stdlib/bindings (riesgo medio)

1. Endurecer política de colisiones en entornos productivos (`namespace_required`).
2. Completar cobertura contractual por módulo stdlib y backend.
3. Añadir checks de trazabilidad de metadata de import y bridge runtime.

### Bloque 4 — Retiro legacy interno (riesgo medio/alto)

1. Medir uso de backends legacy en CI y repos downstream.
2. Desactivar por defecto rutas legacy fuera de perfiles internos.
3. Eliminar componentes obsoletos por release, con rollback claro.

### Bloque 5 — Cierre y escalabilidad (riesgo medio)

1. Publicar ADR final de “Cobra-only UX”.
2. Establecer policy-check automático doc↔CLI↔contrato.
3. Definir roadmap de evolución de stdlib sobre Python/JS/Rust únicamente.
