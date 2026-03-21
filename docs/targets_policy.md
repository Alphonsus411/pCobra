# Política oficial de targets

Este documento define la política de lenguajes soportados que debe mantenerse coherente entre código, CLI, CI y documentación pública.

## Fuente de verdad

La fuente única de verdad para los targets oficiales de salida es `src/pcobra/cobra/transpilers/targets.py`. En ese módulo se definen explícitamente:

- `TIER1_TARGETS`
- `TIER2_TARGETS`
- `OFFICIAL_TARGETS`
- helpers como `normalize_target_name`, `target_cli_choices` y `build_target_help_by_tier`

El registro canónico de clases está en `src/pcobra/cobra/transpilers/registry.py`.

La separación entre **targets oficiales de transpilación** y **targets con runtime oficial** se aplica hoy en `src/pcobra/cobra/cli/target_policies.py`.

## Salida directa oficial

Los únicos destinos oficiales de `cobra compilar` son:

### Tier 1

1. `python`
2. `rust`
3. `javascript`
4. `wasm`

### Tier 2

1. `go`
2. `cpp`
3. `java`
4. `asm`

## Política de nombres canónicos

En documentación pública, ejemplos de CLI, tablas, archivos de configuración y texto narrativo deben usarse exclusivamente los nombres canónicos:

- `python`
- `rust`
- `javascript`
- `wasm`
- `go`
- `cpp`
- `java`
- `asm`

No se deben publicar aliases legacy ni targets retirados en snippets o tablas de usuario final.

## Reverse de entrada

La transpilación inversa se documenta como capacidad independiente. Su política de entrada se define en `src/pcobra/cobra/transpilers/reverse/policy.py`.

Los orígenes reverse canónicos vigentes son:

- `python`
- `javascript`
- `java`

La documentación pública no debe reintroducir el antiguo origen reverse asociado a WASM ni otros orígenes retirados.

## Separación explícita entre transpilación y ejecución

Los 8 targets oficiales de salida representan el alcance de **transpilación** del proyecto. Eso no implica paridad automática de ejecución.

### Targets oficiales con runtime/tooling de ejecución

Los únicos targets con runtime Docker oficial en la CLI y en `src/pcobra/core/sandbox.py` son:

- `python`
- `javascript`
- `cpp`
- `rust`

La verificación ejecutable (`cobra verificar`) se limita actualmente a:

- `python`
- `javascript`

### Targets oficiales solo de generación

Los siguientes backends son oficiales para generar código, pero no deben documentarse como runtimes Docker/sandbox oficiales:

- `wasm`
- `go`
- `java`
- `asm`

## Compatibilidad contractual mínima

La política pública de compatibilidad por feature se resume en `src/pcobra/cobra/transpilers/compatibility_matrix.py`.

A día de hoy:

- `python` es `full` para `holobit`, `proyectar`, `transformar`, `graficar`, `corelibs` y `standard_library`.
- `javascript` es `full` para primitivas Holobit y `partial` para `corelibs`/`standard_library`.
- `rust`, `wasm`, `go`, `cpp`, `java` y `asm` están en `partial` para todas las features contractuales actuales.

Esto debe interpretarse como **contrato de generación y hooks/fallbacks**, no como promesa universal de ejecución equivalente entre backends.

## Packaging y prerrequisitos que afectan al alcance real

- `pyproject.toml` declara `holobit-sdk==1.0.8` solo para Python `>=3.10`.
- El runtime JavaScript y su sandbox dependen además del entorno (`node`, `vm2` y, en ciertas pruebas contractuales, `node-fetch`).
- `Makefile` solo construye contenedores oficiales para `python`, `javascript`, `cpp` y `rust`.

## Regla de mantenimiento

- No se deben documentar otros lenguajes como targets oficiales de salida.
- El registro de transpiladores (`registry.py`), la CLI (`compile_cmd.py`) y la matrix contractual (`compatibility_matrix.py`) deben mantenerse alineados con `OFFICIAL_TARGETS`.
- La CI debe incluir comprobaciones textuales para impedir la reaparición de aliases legacy, módulos reverse borrados, extras no vigentes o ejemplos de CLI fuera de política en rutas de documentación pública y ejemplos.
- Cualquier ampliación o reducción del alcance debe actualizar:
  - este archivo,
  - la fuente de verdad en código,
  - y la validación automática en CI.

## Comprobaciones verificables

```bash
python scripts/ci/validate_targets.py
python -m pytest tests/unit/test_official_targets_consistency.py
python -m pytest tests/unit/test_cli_target_aliases.py
python -m pytest tests/unit/test_holobit_backend_contract_matrix.py
python -m pytest tests/integration/transpilers/test_official_backends_tier1.py
python -m pytest tests/integration/transpilers/test_official_backends_tier2.py
python -m pytest tests/integration/transpilers/test_official_backends_contracts.py
```
