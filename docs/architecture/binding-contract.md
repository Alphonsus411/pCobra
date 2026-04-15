# Contrato de bindings Cobra (Python / JavaScript / Rust)

- **Estado:** Aprobado
- **Fecha:** 2026-04-14
- **Alcance:** CLI runners (`execute_cmd`) y futuros runners/runtime bridges

## Objetivo

Definir un contrato técnico único para evitar lógica ad-hoc en runners sobre cómo conectar Cobra con cada runtime soportado.

## Rutas oficiales de binding

### 1) Python: import bridge directo

- **Ruta contractual:** `python_direct_import`
- **Estrategia:** importación directa de módulos Python canónicos desde el proceso de ejecución Cobra.
- **Frontera de ejecución:** mismo proceso.
- **Contrato:** API Python estable + typing.

### 2) JavaScript: runtime bridge (proceso/VM controlada)

- **Ruta contractual:** `javascript_runtime_bridge`
- **Estrategia:** bridge hacia runtime JS dedicado (proceso o VM controlada).
- **Frontera de ejecución:** aislada respecto al proceso principal.
- **Contrato:** mensajes/IPC versionados.

### 3) Rust: bindings compilados / FFI con ABI estable

- **Ruta contractual:** `rust_compiled_ffi`
- **Estrategia:** bindings compilados sobre librería compartida.
- **Frontera de ejecución:** interfaz nativa FFI.
- **Contrato:** ABI estable y versionada.

## Módulo técnico

Se establece como fuente de verdad:

- `src/pcobra/cobra/bindings/contract.py`

Este módulo expone:

- `BindingRoute` (enum de rutas),
- `BindingCapabilities` (tipo estructurado de capacidades),
- contratos concretos para `python`, `javascript`, `rust`,
- `resolve_binding(language)` para consumo uniforme desde runners.

## Consumo en runners

- `execute_cmd.py` consume `RuntimeManager` para:
  - resolver contrato + bridge,
  - validar seguridad por ruta (`python_direct_import`, `javascript_runtime_bridge`, `rust_compiled_ffi`),
  - validar ABI efectiva por backend.
- `build/backend_pipeline.py` expone `resolve_backend_runtime(...)` y agrega `runtime` al resultado de `build(...)` para que los flujos de compilación tengan metadatos de compatibilidad.
- Runners futuros deben consumir `RuntimeManager` para decidir la ruta técnica sin duplicar reglas.

## Contrato de versionado ABI

- **Versión de ABI actual:** `1.0`
- **Regla de compatibilidad:** una ruta solo es compatible si su `abi_version` está en el conjunto soportado por esa ruta.
- **Punto de validación:** `RuntimeManager.validate_abi_route(language, abi_version)`.

### Tabla de compatibilidad ABI por backend

| Backend | Ruta contractual | Contrato ABI/API | ABI soportadas |
|---|---|---|---|
| Python | `python_direct_import` | API pública Python + typing estable | `1.0` |
| JavaScript | `javascript_runtime_bridge` | Mensajería/IPC versionada | `1.0` |
| Rust | `rust_compiled_ffi` | ABI nativa estable/versionada | `1.0` |

## Validaciones de seguridad por ruta

- `python_direct_import`: ejecución en proceso local, no se considera ruta containerizada.
- `javascript_runtime_bridge`: requiere runtime gestionado (sandbox o contenedor) para preservar aislamiento.
- `rust_compiled_ffi`: frontera nativa FFI; no se ejecuta como sandbox Python directo.

## Regla de evolución

Si se añade un backend oficial nuevo:

1. actualizar `contract.py`,
2. documentar la ruta en este documento,
3. adoptar `resolve_binding(...)` en el runner correspondiente.
