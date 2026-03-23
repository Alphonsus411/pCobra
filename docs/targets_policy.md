# Política oficial de targets

Este documento fija la narrativa pública canónica de pCobra: el proyecto **transpila únicamente a 8 backends oficiales** agrupados en **Tier 1** y **Tier 2**. Cualquier otra denominación, alias, artefacto de implementación o target retirado queda fuera de las páginas públicas activas.

## Fuente única de verdad

La fuente única de verdad para los backends oficiales de salida es `src/pcobra/cobra/transpilers/targets.py`.

Ese módulo define exactamente:

- `TIER1_TARGETS`
- `TIER2_TARGETS`
- `OFFICIAL_TARGETS`
- helpers canónicos como `normalize_target_name`, `target_cli_choices`, `build_target_help_by_tier` y `official_target_rows`

La política operativa de runtime, Holobit y SDK se deriva de `src/pcobra/cobra/cli/target_policies.py` y `src/pcobra/cobra/transpilers/compatibility_matrix.py`.

## Lista exacta de backends oficiales

`OFFICIAL_TARGETS` debe ser siempre la concatenación exacta de `TIER1_TARGETS + TIER2_TARGETS`.

### Tier 1

- `python`
- `rust`
- `javascript`
- `wasm`

### Tier 2

- `go`
- `cpp`
- `java`
- `asm`

En CLI, documentación, ejemplos, tablas y configuración pública **solo** se aceptan esos 8 nombres canónicos.

## Estado público por backend

| Backend | Tier | Runtime público | Estado Holobit público | Compatibilidad SDK real |
|---|---|---|---|---|
| `python` | Tier 1 | oficial verificable | `full`; usa el contrato completo del SDK Python | completa |
| `rust` | Tier 1 | oficial verificable | adaptador mantenido por el proyecto; estado contractual `partial` | parcial |
| `javascript` | Tier 1 | oficial verificable | adaptador mantenido por el proyecto; estado contractual `partial` | parcial |
| `wasm` | Tier 1 | solo transpilación | hooks/puentes contractuales `partial`; depende del host | parcial |
| `go` | Tier 2 | best-effort no público | hooks/adaptadores `partial` sobre runtime best-effort | parcial |
| `cpp` | Tier 2 | oficial verificable | adaptador mantenido por el proyecto; estado contractual `partial` | parcial |
| `java` | Tier 2 | best-effort no público | hooks/adaptadores `partial` sobre runtime best-effort | parcial |
| `asm` | Tier 2 | solo transpilación | hooks simbólicos/diagnóstico `partial`; requiere runtime externo | parcial |

Lectura normativa de la tabla:

- `python` es el único backend que puede presentarse como compatibilidad SDK completa.
- `rust`, `javascript` y `cpp` tienen runtime oficial verificable y adaptador Holobit mantenido, pero **siguen siendo `partial`** a nivel contractual.
- `go` y `java` siguen siendo backends oficiales de salida con runtime best-effort, pero no deben describirse como equivalentes a un runtime oficial público ni a compatibilidad SDK completa.
- `wasm` y `asm` siguen siendo backends oficiales de salida solo de transpilación, pero no deben describirse como equivalentes a un runtime oficial público ni a compatibilidad SDK completa.

## Alcance del contrato

Los 8 nombres de `OFFICIAL_TARGETS` describen el alcance oficial de **transpilación de salida**.

Eso no implica que todos los backends prometan el mismo runtime ni la misma cobertura de librerías. La separación pública correcta es:

- `OFFICIAL_RUNTIME_TARGETS`: `python`, `rust`, `javascript`, `cpp`
- `VERIFICATION_EXECUTABLE_TARGETS`: `python`, `rust`, `javascript`, `cpp`
- `BEST_EFFORT_RUNTIME_TARGETS`: `go`, `java`
- `TRANSPILATION_ONLY_TARGETS`: `wasm`, `asm`
- `NO_RUNTIME_TARGETS`: `wasm`, `asm`
- `OFFICIAL_STANDARD_LIBRARY_TARGETS`: `python`, `rust`, `javascript`, `cpp`
- `ADVANCED_HOLOBIT_RUNTIME_TARGETS`: `python`, `rust`, `javascript`, `cpp`
- `SDK_COMPATIBLE_TARGETS`: `python`

La matriz contractual por backend y feature vive en `src/pcobra/cobra/transpilers/compatibility_matrix.py` y se publica en `docs/matriz_transpiladores.md`.

## Reglas de redacción pública

La documentación pública activa debe respetar estas reglas editoriales:

1. Presentar siempre una sola narrativa: pCobra transpila a **8 backends oficiales**.
2. Nombrar únicamente los identificadores canónicos `python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java` y `asm`.
3. Distinguir explícitamente entre **transpilación oficial**, **runtime oficial verificable**, **runtime best-effort no público** y **solo transpilación**.
4. Describir Holobit solo con el contrato vigente: `python` `full`; el resto, como máximo, `partial` según la matriz contractual.
5. No presentar a ningún backend distinto de `python` como compatibilidad SDK completa.

## Reverse

La transpilación inversa se documenta como capacidad separada. Sus orígenes de entrada se definen en `src/pcobra/cobra/transpilers/reverse/policy.py`.

Esos orígenes reverse **no amplían** `OFFICIAL_TARGETS`: describen entradas aceptadas por `cobra transpilar-inverso`, no targets oficiales de salida. La documentación pública debe hablar de **orígenes reverse** y dejar claro que no son targets de salida.

## Archivo histórico y experimentos

Cualquier resto histórico o experimental debe vivir fuera del recorrido normativo principal. Las ubicaciones explícitas para ello son:

- `archive/retired_targets/`
- `docs/historico/`
- `docs/experimental/`

Esas rutas pertenecen al repositorio solo como archivo o material experimental, no como definición vigente del producto final.

## Revisión editorial final

Queda **prohibido reintroducir** en páginas públicas activas:

- alias o nombres alternativos de targets,
- referencias a targets retirados como si siguieran vigentes,
- terminología de arquitectura interna presentada como si fuera un backend público,
- comparativas que inflen el soporte Holobit o la compatibilidad SDK.

La única excepción permitida es una sección **claramente separada** de changelog, historial o nota de migración.

## Qué valida automáticamente el repositorio

La política simplificada valida únicamente estos puntos:

1. `TIER1_TARGETS`, `TIER2_TARGETS` y `OFFICIAL_TARGETS` coinciden exactamente.
2. Los registros y artefactos oficiales (`registry.py`, CLI, módulos `to_*.py`, módulos reverse dentro de su scope, golden files y documentación derivada) permanecen alineados con esos 8 backends.
3. La documentación pública y los textos vigilados no reintroducen aliases públicos no canónicos ni estados incompatibles con la matriz contractual.

## Documentación derivada

Los artefactos derivados deben regenerarse desde la política simplificada:

- `docs/_generated/target_policy_summary.md`
- `docs/_generated/target_policy_summary.rst`
- `docs/_generated/official_targets_table.rst`
- `docs/_generated/runtime_capability_matrix.rst`
- `docs/_generated/reverse_scope_table.rst`
- `docs/_generated/cli_backend_examples.rst`
- `docs/matriz_transpiladores.md`

## Comprobaciones recomendadas

```bash
python scripts/generate_target_policy_docs.py
python scripts/generar_matriz_transpiladores.py
python scripts/validate_targets_policy.py
python scripts/ci/validate_targets.py
python -m pytest tests/unit/test_validate_targets_policy_script.py
python -m pytest tests/unit/test_official_targets_consistency.py
```
