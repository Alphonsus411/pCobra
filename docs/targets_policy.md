# Política oficial de targets

Este documento define la política de lenguajes soportados que debe mantenerse coherente entre código, CLI, CI y documentación pública.

## Fuente de verdad

La fuente única de verdad para los targets oficiales de salida es `src/pcobra/cobra/transpilers/targets.py`. En ese módulo se definen explícitamente:

- `TIER1_TARGETS`
- `TIER2_TARGETS`
- `OFFICIAL_TARGETS`
- helpers como `normalize_target_name`, `target_cli_choices` y `build_target_help_by_tier`

El registro canónico de clases está en `src/pcobra/cobra/transpilers/registry.py`.

La separación entre **targets oficiales de transpilación** y **targets con runtime oficial** se aplica hoy en `src/pcobra/cobra/cli/target_policies.py`, que debe citarse junto con `src/pcobra/cobra/transpilers/targets.py` en documentación pública para evitar divergencias.

## Salida directa oficial

Los únicos destinos oficiales de `cobra compilar` son la lista canónica completa:

- `python`
- `rust`
- `javascript`
- `wasm`
- `go`
- `cpp`
- `java`
- `asm`

Estos 8 nombres son la referencia pública completa antes de separarlos por tier.

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

La transpilación inversa se documenta como capacidad independiente. Su política de **orígenes de entrada** se define en `src/pcobra/cobra/transpilers/reverse/policy.py`.

Los orígenes reverse canónicos vigentes son:

- `python`
- `javascript`
- `java`

Estos nombres describen **lenguajes de entrada para `cobra transpilar-inverso`**, no targets oficiales de salida. La documentación pública no debe mezclar ambas categorías ni reintroducir el antiguo origen reverse asociado a WASM u otros orígenes retirados.

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
- `javascript` es `partial` para primitivas Holobit, `corelibs` y `standard_library`: genera hooks `cobra_*`, conserva la colección base en `cobra_holobit` y falla explícitamente en operaciones avanzadas; no debe venderse como compatibilidad SDK completa.
- `rust`, `wasm`, `go`, `cpp`, `java` y `asm` están en `partial` para todas las features contractuales actuales.

Esto debe interpretarse como **contrato de generación y hooks/fallbacks**, no como promesa universal de ejecución equivalente entre backends.

## Experimentos y material histórico

Los contenidos que describan pipelines, parsers reverse o prototipos fuera de los 8 targets oficiales deben mantenerse fuera de la documentación principal o marcados explícitamente. Ningún enlace desde la documentación principal hacia `docs/experimental/` o `docs/historico/` debe aparecer sin etiquetas visibles como `experimental`, `interno`, `fuera de política` o `histórico`.

Ubicaciones autorizadas:

- `docs/experimental/`: experimentos, prototipos o referencias de investigación.
- `docs/historico/`: material archivado sin vigencia normativa.

Ejemplos actuales de documentación segregada:

- prototipo LLVM;
- notas de mapeo a LLVM IR;
- soporte reverse desde LaTeX;
- referencia retirada del reverse desde WASM en `docs/experimental/limitaciones_wasm_reverse.md`.

Los IR internos o pipelines auxiliares solo pueden mencionarse en la documentación principal como arquitectura interna del compilador, nunca como targets oficiales de salida ni como orígenes reverse mantenidos por política. Las guías dedicadas a esos artefactos deben permanecer fuera de la navegación pública principal y etiquetarse como documentación experimental o de mantenimiento.

## Packaging y prerrequisitos que afectan al alcance real

- `pyproject.toml` declara `holobit-sdk==1.0.8` como dependencia obligatoria para instalaciones con Python `>=3.10`.
- El runtime JavaScript y su sandbox dependen además del entorno (`node`, `vm2` y, en ciertas pruebas contractuales, `node-fetch`).
- `Makefile` solo construye contenedores oficiales para `python`, `javascript`, `cpp` y `rust`.

## Regla de mantenimiento

- No se deben documentar otros lenguajes como targets oficiales de salida.
- El registro de transpiladores (`registry.py`), la CLI (`compile_cmd.py`) y la matrix contractual (`compatibility_matrix.py`) deben mantenerse alineados con `OFFICIAL_TARGETS`.
- La CI debe incluir comprobaciones textuales para impedir la reaparición de aliases legacy, módulos reverse borrados, extras no vigentes, ejemplos de CLI fuera de política o documentación experimental presentada como soporte oficial.
- Cualquier ampliación o reducción del alcance debe actualizar:
  - este archivo,
  - la fuente de verdad en código,
  - y la validación automática en CI.

## Cobertura exacta de la validación automática

La validación automática de política/targets vigila de forma explícita estos árboles y documentos:

- `README.md`
- `docs/`
- `docs/proposals/` (tratadas como documentación activa mientras no se archiven en `docs/historico/` o `docs/experimental/`)
- `docs/MANUAL_COBRA.md`
- `tests/utils/`
- `tests/performance/`
- `tests/integration/`
- `scripts/`
- `src/pcobra/cobra/cli/commands/compile_cmd.py`
- `src/pcobra/cobra/cli/commands/benchmarks_cmd.py`
- `src/pcobra/cobra/cli/target_policies.py`

Dentro de ese alcance la CI comprueba, como mínimo:

- que no reaparezcan aliases legacy presentados como válidos (véase `docs/historico/targets_aliases_legacy.md`, histórico);
- que no queden ramas activas, módulos o condicionales para backends retirados/fuera de política como el backend retirado de C;
- que las listas públicas y/o hardcodeadas de runtime, transpilación, verificación y reverse sigan alineadas con `target_policies.py`, `targets.py` y `reverse/policy.py`;
- que la documentación pública sobre Holobit (`README.md`, `docs/MANUAL_COBRA.md`, `docs/contrato_runtime_holobit.md`, `docs/matriz_transpiladores.md`, `docs/targets_policy.md`) no promocione compatibilidad superior a la matriz contractual;
- que las tablas contractuales de Holobit sigan idénticas a `src/pcobra/cobra/transpilers/compatibility_matrix.py`.

Las únicas exclusiones históricas explícitas permitidas son:

- `docs/experimental/`
- `docs/historico/`

Todo contenido fuera de esas carpetas debe considerarse vigente y sujeto a la política oficial.

En particular, `docs/proposals/` queda dentro del alcance vigilado: si una propuesta sigue activa, debe usar nombres canónicos, rutas actuales y no presentar targets experimentales como públicos.

## Comprobaciones verificables

```bash
python scripts/ci/validate_targets.py
python scripts/validate_targets_policy.py
python -m pytest tests/unit/test_official_targets_consistency.py
python -m pytest tests/unit/test_cli_target_aliases.py
python -m pytest tests/unit/test_public_docs_scope.py
python -m pytest tests/unit/test_holobit_backend_contract_matrix.py
python -m pytest tests/integration/transpilers/test_official_backends_tier1.py
python -m pytest tests/integration/transpilers/test_official_backends_tier2.py
python -m pytest tests/integration/transpilers/test_official_backends_contracts.py
```
