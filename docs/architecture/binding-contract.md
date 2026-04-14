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

- `execute_cmd.py` debe resolver contrato vía `resolve_binding(...)` para runtime Python y ejecución en contenedor.
- Runners futuros deben consumir este contrato para decidir la ruta técnica sin duplicar reglas.

## Regla de evolución

Si se añade un backend oficial nuevo:

1. actualizar `contract.py`,
2. documentar la ruta en este documento,
3. adoptar `resolve_binding(...)` en el runner correspondiente.
