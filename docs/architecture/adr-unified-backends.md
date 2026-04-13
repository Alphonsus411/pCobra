# ADR: Unificación de backends públicos en Cobra

- **Estado:** Aprobado
- **Fecha:** 2026-04-13
- **Decisores:** Equipo Core de pCobra
- **Relacionado con:** política de targets, CLI pública, documentación de onboarding

## Contexto

La superficie pública de backends había crecido mezclando objetivos distintos:

- targets oficialmente soportados para usuarios finales,
- targets mantenidos por compatibilidad histórica,
- y targets útiles para experimentación interna.

Esa mezcla introducía ambigüedad en documentación, CLI y expectativas de soporte.

## Decisión

1. **Cobra es la única interfaz pública del proyecto** para compilación/transpilación y ejecución de flujos soportados.
2. Los **únicos backends oficiales públicos** pasan a ser:
   - `python`
   - `javascript`
   - `rust`
3. Los targets `go`, `cpp`, `java`, `wasm` y `asm` se clasifican como **`legacy/internal`**:
   - no son parte de la promesa pública,
   - no deben promocionarse en documentación de usuario,
   - pueden existir para migración, compatibilidad o uso interno.

## Impacto técnico (mapeo solicitado)

### 1) `src/pcobra/cobra/config/transpile_targets.py`

- `ALLOWED_TARGETS` se reduce a `python`, `javascript`, `rust`.
- Se introduce `LEGACY_INTERNAL_TARGETS` con `go`, `cpp`, `java`, `wasm`, `asm`.
- La validación canónica asegura:
  - que el canon público y metadatos solo cubran los 3 backends oficiales,
  - que no exista solape entre oficiales y `legacy/internal`.

### 2) `src/pcobra/cobra/cli/target_policies.py`

- Las categorías públicas (`OFFICIAL_RUNTIME_TARGETS`, `BEST_EFFORT_RUNTIME_TARGETS`, `TRANSPILATION_ONLY_TARGETS`, `SDK_COMPATIBLE_TARGETS`) se filtran contra el canon oficial actual.
- Se añade categoría visible de `legacy/internal` para trazabilidad (`LEGACY_INTERNAL_TARGETS`).
- Resultado práctico:
  - `OFFICIAL_TRANSPILATION_TARGETS`: `python`, `javascript`, `rust`.
  - `BEST_EFFORT_RUNTIME_TARGETS` y `TRANSPILATION_ONLY_TARGETS` pueden quedar vacíos en superficie pública.

### 3) `README.md`

- Se actualiza la narrativa para declarar explícitamente:
  - Cobra como interfaz pública,
  - solo 3 backends oficiales (`python`, `javascript`, `rust`),
  - resto como `legacy/internal`.
- Se incluye guía de migración de targets legacy hacia los 3 backends oficiales.

## Consecuencias

### Positivas

- Menor ambigüedad contractual para usuarios y contribuyentes.
- Más foco en calidad y testing de los 3 backends oficiales.
- Documentación pública más coherente con soporte real.

### Negativas / trade-offs

- Consumidores que dependan de `go/cpp/java/wasm/asm` deben migrar su operación principal.
- Requiere actualizar ejemplos antiguos y pipelines que asumían esos targets como públicos.

## Plan de migración desde targets legacy

Targets legacy afectados: `go`, `cpp`, `java`, `wasm`, `asm`.

### Ruta recomendada

1. **Inventario**
   - Identificar comandos/pipelines que usen `--backend go|cpp|java|wasm|asm`.
2. **Selección de backend oficial destino**
   - Elegir `python`, `javascript` o `rust` según runtime y ecosistema requerido.
3. **Actualización de CLI/configuración**
   - Sustituir backend legacy por backend oficial en scripts, CI y documentación interna.
4. **Verificación funcional**
   - Ejecutar pruebas de regresión equivalentes con el backend oficial escogido.
5. **Retirada progresiva**
   - Mantener fallback legacy temporal solo para contingencias internas, sin exposición pública.

### Recomendaciones de mapeo inicial

- `go` ⟶ `rust` o `python`.
- `cpp` ⟶ `rust`.
- `java` ⟶ `javascript` o `python`.
- `wasm` ⟶ `javascript` (si el objetivo principal es entorno web/runtime JS) o `rust`.
- `asm` ⟶ `rust` (si se necesita control de bajo nivel dentro del conjunto oficial).

## Estado de cumplimiento

Este ADR queda implementado en configuración central, políticas CLI y README.
