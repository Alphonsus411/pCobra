# Checklist operativa de limpieza de targets

Este documento define el **inventario canónico** y las reglas de aceptación para cambios de política de targets. Se utiliza como contrato humano y como entrada de validación automática en `scripts/ci/validate_targets.py`.

## Inventario por categoría

### 1) Módulos `to_*.py`

<!-- BEGIN to_modules -->
- `src/pcobra/cobra/transpilers/transpiler/to_asm.py`
- `src/pcobra/cobra/transpilers/transpiler/to_cpp.py`
- `src/pcobra/cobra/transpilers/transpiler/to_go.py`
- `src/pcobra/cobra/transpilers/transpiler/to_java.py`
- `src/pcobra/cobra/transpilers/transpiler/to_js.py`
- `src/pcobra/cobra/transpilers/transpiler/to_python.py`
- `src/pcobra/cobra/transpilers/transpiler/to_rust.py`
- `src/pcobra/cobra/transpilers/transpiler/to_wasm.py`
<!-- END to_modules -->

### 2) Carpetas `*_nodes`

<!-- BEGIN nodes_dirs -->
- `src/pcobra/cobra/transpilers/transpiler/asm_nodes`
- `src/pcobra/cobra/transpilers/transpiler/cpp_nodes`
- `src/pcobra/cobra/transpilers/transpiler/go_nodes`
- `src/pcobra/cobra/transpilers/transpiler/java_nodes`
- `src/pcobra/cobra/transpilers/transpiler/js_nodes`
- `src/pcobra/cobra/transpilers/transpiler/python_nodes`
- `src/pcobra/cobra/transpilers/transpiler/rust_nodes`
<!-- END nodes_dirs -->

### 3) Goldens en `tests/integration/transpilers/golden/`

<!-- BEGIN golden_files -->
- `tests/integration/transpilers/golden/asm.golden`
- `tests/integration/transpilers/golden/cpp.golden`
- `tests/integration/transpilers/golden/go.golden`
- `tests/integration/transpilers/golden/java.golden`
- `tests/integration/transpilers/golden/javascript.golden`
- `tests/integration/transpilers/golden/python.golden`
- `tests/integration/transpilers/golden/rust.golden`
- `tests/integration/transpilers/golden/wasm.golden`
<!-- END golden_files -->

### 4) Políticas (CLI, benchmark, docker, docs)

#### CLI
<!-- BEGIN policy_cli -->
- `src/pcobra/cobra/cli/commands/compile_cmd.py`
- `src/pcobra/cobra/cli/commands/benchmarks_cmd.py`
- `src/pcobra/cobra/cli/target_policies.py`
<!-- END policy_cli -->

#### Benchmark
<!-- BEGIN policy_benchmark -->
- `scripts/benchmarks/targets_policy.py`
- `scripts/benchmarks/run_benchmarks.py`
- `docs/frontend/benchmarking.rst`
<!-- END policy_benchmark -->

#### Docker
<!-- BEGIN policy_docker -->
- `docker/backends/python.Dockerfile`
- `docker/backends/javascript.Dockerfile`
- `docker/backends/cpp.Dockerfile`
- `docker/backends/rust.Dockerfile`
- `docs/frontend/contenedores.rst`
<!-- END policy_docker -->

#### Docs
<!-- BEGIN policy_docs -->
- `README.md`
- `docs/targets_policy.md`
- `docs/matriz_transpiladores.md`
- `docs/contrato_runtime_holobit.md`
- `docs/frontend/backends.rst`
- `docs/frontend/cli.rst`
- `docs/frontend/transpilers_tier_plan.md`
<!-- END policy_docs -->


## Narrativa pública obligatoria

La documentación pública activa debe mantener explícitamente:

- la frase de **8 targets oficiales de salida** (sin alias legacy),
- la **separación entre transpilación de salida y reverse de entrada**.

## Reglas de aceptación

1. **Sin archivo extra:** no se acepta ningún `to_*.py`, `*_nodes` o `.golden` fuera del inventario canónico.
2. **Sin cadena legacy en docs públicas:** no se aceptan aliases legacy ni referencias a backends/pipelines retirados en documentación pública activa.
3. **Sin comandos CLI fuera del set canónico:** en documentos de política de targets solo se permiten:

<!-- BEGIN canonical_cli_commands -->
- `cobra compilar`
- `cobra verificar`
- `cobra benchmarks`
- `cobra transpilar-inverso`
<!-- END canonical_cli_commands -->

## Uso de mantenimiento

Antes de fusionar cambios de política:

1. Actualizar este checklist si cambia el contrato oficial.
2. Ejecutar `python scripts/ci/validate_targets.py`.
3. Corregir cualquier desalineación antes de mergear.

## Checklist de ejecución por fases (bloqueante para merge)

> Estado objetivo: si cualquier casilla queda sin marcar, `scripts/ci/validate_targets.py` debe fallar y bloquear el merge.

### Fase 1 — Hardening de whitelist canónica (CLI + registry + benchmarks policy)
- [x] `OFFICIAL_TARGETS`, registro y `LANG_CHOICES` están alineados.
- [x] `scripts/benchmarks/targets_policy.py` valida metadata solo para targets oficiales.
- [x] No existen aliases públicos fuera de política canónica.

### Fase 2 — Limpieza de restos en docs/scripts/tests + regeneración de derivados
- [x] No hay `to_*.py` extra fuera del inventario canónico.
- [x] No hay `*_nodes` extra fuera del inventario canónico.
- [x] No hay `.golden` extra fuera del inventario canónico.
- [x] Packaging (`MANIFEST.in`/`pyproject.toml`) excluye explícitamente históricos y experimentales no distribuibles.
- [x] Se regeneraron artefactos derivados de docs cuando aplica (`scripts/generate_target_policy_docs.py`).

### Fase 3 — Consolidación del contrato Holobit/SDK y mensajes públicos
- [x] Solo `python` se comunica como compatibilidad SDK completa.
- [x] Backends no Python mantienen narrativa contractual `partial`.
- [x] Las tablas públicas de contrato Holobit/SDK siguen sincronizadas con la matriz canónica.

### Fase 4 — Depuración de adaptadores/código muerto + actualización de goldens
- [x] No hay adaptadores legacy fuera de rutas históricas permitidas.
- [x] El árbol activo de transpiladores está limitado al contrato de 8 backends.
- [x] Los goldens oficiales existen y corresponden exactamente al set canónico.

### Fase 5 — Validación final integral en CI
- [x] Política de targets validada (`python scripts/ci/validate_targets.py`).
- [x] Coherencia de docs públicas validada (`python scripts/validate_targets_policy.py`).
- [x] Contrato de compatibilidad por backend validado (`python scripts/validate_runtime_contract.py`).
- [x] Cualquier guardrail en fallo bloquea merge (jobs CI en estado failed).
