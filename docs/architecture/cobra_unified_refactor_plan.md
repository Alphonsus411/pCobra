# Plan de arquitectura y refactor parcial seguro: Cobra Ecosystem Unified

## Contrato unificado (aplica a todo el plan)

- Cobra es el **único lenguaje/interfaz pública**.
- Solo existen **3 backends internos oficiales**: `python`, `javascript`, `rust`.
- La decisión de backend es **interna** (no configurable por usuario final), salvo hints internos controlados.

Este documento define una estrategia **incremental** para consolidar Cobra como único lenguaje visible para usuario final, con tres backends oficiales internos: `python`, `javascript` y `rust`.

> Restricciones aplicadas en este plan: no tocar lexer, parser, AST ni transpilers existentes.

---

## A) Architecture overview

### Objetivo macro
- **Entrada única**: usuario escribe y opera solamente en Cobra.
- **Backends oficiales internos**: Python, JavaScript y Rust.
- **Transpilación oculta**: la CLI pública no expone selección manual de transpiler.
- **Contrato de stdlib**: módulos públicos orientados por backend primario y fallbacks controlados.

### Capas objetivo
1. **Frontend de lenguaje (intocable)**: lexer/parser/AST.
2. **Orquestación interna**: `build.backend_pipeline`, `build.orchestrator`, adapters de backend.
3. **Bindings runtime**: rutas Python direct import, JS runtime bridge, Rust FFI.
4. **CLI pública mínima**: `run`, `build`, `test`, `mod`.

---

## B) Core module alignment

### Estado contractual
- Fuente pública de verdad de backends: `PUBLIC_BACKENDS = (python, javascript, rust)`.
- Backends legacy se mantienen solo en modo compatibilidad interna.

### Alineación propuesta
- Mantener front-end intacto.
- Reforzar que cualquier ruta pública consulte `PUBLIC_BACKENDS`.
- Tratar módulos legacy como **inventario de retiro**, no como opciones para usuario final.

### Candidatos legacy a retirar
- `go`, `cpp`, `java`, `wasm`, `asm`.

---

## C) CLI redesign

### UX pública objetivo
```bash
cobra run archivo.cobra
cobra build archivo.cobra
cobra test archivo.cobra
cobra mod list
```

### Reglas
- El usuario no indica transpiler directamente en la CLI pública v2.
- Los comandos legacy quedan encapsulados para migración interna, fuera de la UX pública principal.

---

## D) Transpiler integration

### Enfoque
- No modificar transpilers existentes.
- Invocarlos por una única fachada interna (`backend_pipeline` / adapters).

### Selección backend interna
1. Resolver backend por orquestador y contexto (archivo/capacidades).
2. Validar ruta runtime (ABI + seguridad).
3. Invocar transpiler oficial correspondiente.

---

## E) Stdlib design

### Módulos públicos
- `cobra.core`: base transversal.
- `cobra.datos`: prioridad Python.
- `cobra.web`: prioridad JavaScript.
- `cobra.system`: híbrido Python/Rust con fallback JS.

### Política
- API Cobra estable para el usuario.
- Implementación interna guiada por `stdlib_contract`.
- Fallbacks explícitos y auditables.

---

## F) Import system

### Casos requeridos
1. **Import Python bridge**: `importar pandas`.
2. **Import stdlib Cobra**: `importar datos` / `importar cobra.datos`.
3. **Módulos híbridos**: mapeados por configuración.

### Orden de resolución
1. `stdlib`
2. `project`
3. `python_bridge`
4. `hybrid`

### Conflictos
- Modo transición: `warn`.
- Producción recomendada: `namespace_required`.

### Inyección
- Adjuntar metadata de resolución y `backend_adapter` al módulo cargado.

---

## G) Binding system

### Rutas contractuales
- **Python**: `python_direct_import`.
- **JavaScript**: `javascript_runtime_bridge`.
- **Rust**: `rust_compiled_ffi`.

### Validaciones mínimas
- Seguridad por comando (`run`/`test`).
- Negociación ABI por backend.
- Selección de bridge consistente por ruta.

---

## H) Elements to remove (safe retirement backlog)

> Fasear en releases para evitar ruptura.

1. Comandos CLI ligados a targets retirados (solo tras auditoría de uso).
2. Scripts de benchmark/transpilación exclusivos de backends legacy.
3. Documentación pública que mencione targets fuera de `python/javascript/rust`.

---

## I) Documentation updates

Actualizar progresivamente:
- `README.md`:
  - Cobra como interfaz única.
  - Backends oficiales internos.
  - CLI pública simplificada.
- `docs/architecture/*`:
  - diagrama de capas y rutas de binding.
  - contrato de import/bindings/stdlib.
- Guías de migración:
  - desuso de comandos legacy y rutas directas a transpilers.

---

## Tareas estructuradas (paso a paso)

### Fase 1 — Alineación contractual (bajo riesgo)
1. Validar que rutas públicas usan solo `PUBLIC_BACKENDS`.
2. Publicar inventario de legados y ventana de retiro.
3. Añadir chequeos CI de coherencia contrato ↔ documentación.

### Fase 2 — UX CLI unificada (bajo riesgo)
1. Consolidar documentación oficial alrededor de `run/build/test/mod`.
2. Mantener compatibilidad legacy solo por perfil de desarrollo.
3. Eliminar exposición pública de flags ligados a transpilers.

### Fase 3 — Contrato stdlib/imports/bindings (riesgo medio)
1. Completar cobertura por módulo en `stdlib_contract`.
2. Forzar política de conflictos de imports por entorno.
3. Auditar adapters inyectados y metadatos de resolución.

### Fase 4 — Retiro legacy (riesgo medio/alto)
1. Medir uso de backends legacy en CI/scripts.
2. Retirar comandos/paths obsoletos por lotes pequeños.
3. Validar no regresión con suite de integración.

### Fase 5 — Endurecimiento final
1. Bloquear por defecto rutas internas legacy en builds estables.
2. Documentar sólo arquitectura unificada y bridges oficiales.
3. Publicar changelog de transición cerrada.
