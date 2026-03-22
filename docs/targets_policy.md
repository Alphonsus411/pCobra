# Política oficial de targets

Este documento define el contrato final que debe mantenerse alineado entre código, CLI, CI y documentación pública.

## Fuente única de verdad

La fuente única de verdad para los backends oficiales de salida es `src/pcobra/cobra/transpilers/targets.py`.

Ese módulo define exactamente:

- `TIER1_TARGETS`
- `TIER2_TARGETS`
- `OFFICIAL_TARGETS`
- helpers canónicos como `normalize_target_name`, `target_cli_choices`, `build_target_help_by_tier` y `official_target_rows`

Los 8 backends oficiales son:

- **Tier 1**: `python`, `rust`, `javascript`, `wasm`
- **Tier 2**: `go`, `cpp`, `java`, `asm`

`OFFICIAL_TARGETS` debe ser siempre la concatenación exacta de `TIER1_TARGETS + TIER2_TARGETS`.

## Nombres públicos permitidos

En CLI, documentación, ejemplos, tablas y configuración pública solo se aceptan los 8 nombres canónicos anteriores.

Los nombres heredados o no canónicos no forman parte del contrato público y deben permanecer fuera de la documentación normativa. Si hace falta conservar memoria histórica, debe hacerse únicamente en material archivado como `archive/retired_targets/docs/targets_aliases_legacy.md`, nunca en las guías activas.

La política pública ya no conserva una capa histórica de nombres aceptados ni tablas auxiliares para lenguajes fuera de política.

## Alcance del contrato

Los 8 nombres de `OFFICIAL_TARGETS` describen el alcance oficial de **transpilación de salida**.

Eso no implica que todos los backends prometan el mismo runtime o la misma compatibilidad de librerías. Esa separación vive en `src/pcobra/cobra/cli/target_policies.py`, que deriva subconjuntos públicos como:

- `OFFICIAL_RUNTIME_TARGETS`
- `VERIFICATION_EXECUTABLE_TARGETS`
- `TRANSPILATION_ONLY_TARGETS`
- `BEST_EFFORT_RUNTIME_TARGETS`
- `NO_RUNTIME_TARGETS`
- `OFFICIAL_STANDARD_LIBRARY_TARGETS`
- `ADVANCED_HOLOBIT_RUNTIME_TARGETS`
- `SDK_COMPATIBLE_TARGETS`

La matriz contractual por backend y feature vive en `src/pcobra/cobra/transpilers/compatibility_matrix.py` y se publica en `docs/matriz_transpiladores.md`.

## Compatibilidad contractual mínima

A nivel público, la lectura correcta de la matriz contractual es:

- `python` es el único backend que puede presentarse como `full` para compatibilidad SDK completa.
- Los demás backends oficiales deben presentarse, como máximo, en el nivel contractual `partial` cuando corresponda.
- La documentación pública no debe promocionar a ningún backend distinto de `python` como compatibilidad SDK completa.

## Reverse

La transpilación inversa se documenta como capacidad separada. Sus orígenes de entrada se definen en `src/pcobra/cobra/transpilers/reverse/policy.py`.

Esos orígenes reverse **no amplían** `OFFICIAL_TARGETS`: describen entradas aceptadas por `cobra transpilar-inverso`, no targets oficiales de salida. La documentación pública debe hablar de **orígenes reverse** y dejar claro que no son targets de salida.

## Archivo histórico y experimentos

Cualquier resto histórico o experimental debe vivir fuera del recorrido normativo principal. Las ubicaciones explícitas para ello son:

- `archive/retired_targets/`
- `docs/historico/`
- `docs/experimental/`

Esas rutas pertenecen al árbol principal del repositorio solo como archivo o material experimental, no como definición vigente del producto final.

## Qué valida automáticamente el repositorio

La política simplificada valida únicamente estos puntos:

1. `TIER1_TARGETS`, `TIER2_TARGETS` y `OFFICIAL_TARGETS` coinciden exactamente.
2. Los registros y artefactos oficiales (`registry.py`, CLI, módulos `to_*.py`, módulos reverse dentro de su scope, golden files y documentación derivada) permanecen alineados con esos 8 backends.
3. La documentación pública y los textos vigilados no reintroducen aliases públicos no canónicos.

La validación ya no mantiene reglas dedicadas a restos históricos concretos si no forman parte del producto final.

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
python scripts/validate_targets_policy.py
python scripts/ci/validate_targets.py
python -m pytest tests/unit/test_validate_targets_policy_script.py
python -m pytest tests/unit/test_official_targets_consistency.py
```
