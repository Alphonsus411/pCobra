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
