# Calendario oficial de retiro de backends legacy internos

Este documento toma `INTERNAL_COMPATIBILITY_RETIREMENT_WINDOW` como calendario canónico de deprecación para `go`, `cpp`, `java`, `wasm`, `asm`.

Fuente normativa:

- `src/pcobra/cobra/architecture/backend_policy.py` (`INTERNAL_COMPATIBILITY_RETIREMENT_WINDOW`)
- `src/pcobra/cobra/architecture/legacy_backend_lifecycle.py` (metadatos por backend consumidos por CLI/docs)

## Calendario oficial (canónico)

| Backend | Ventana oficial |
|---|---|
| `go` | `Q4 2026` |
| `cpp` | `Q4 2026` |
| `java` | `Q1 2027` |
| `wasm` | `Q2 2027` |
| `asm` | `Q3 2026` |

## Clasificación de dependencias actuales por backend

> Alcance: comandos (`src/pcobra/cobra/cli/commands`), scripts (`scripts/`) y tests (`tests/`).

### `go`

- **Comandos**: `validar_sintaxis_cmd.py`, `qa_validar_cmd.py`.
- **Scripts**: `targets_policy_common.py`, `audit_retired_targets.py`, `scripts/ci/validate_targets.py`, `scripts/ci/audit_targets_contract.py`, `scripts/ci/generate_internal_only_inventory.py`, y scripts de benchmarks.
- **Tests**: cobertura amplia en unit/integration/performance con foco en contratos de targets internos (ej.: `test_runtime_manager.py`, `test_cli_target_aliases.py`, `test_holobit_backend_contract_matrix.py`).

### `cpp`

- **Comandos**: `verify_cmd.py`, `validar_sintaxis_cmd.py`, `qa_validar_cmd.py`.
- **Scripts**: `targets_policy_common.py`, `hello_clang.py`, `lint_legacy_aliases.py`, `scripts/ci/validate_targets.py`, `scripts/ci/audit_targets_contract.py`.
- **Tests**: cobertura de verificación/ejecución y contratos de targets (ej.: `test_verify_cmd.py`, `test_target_execution_policy.py`, `test_interactive_cmd_sandbox_docker_targets.py`).

### `java`

- **Comandos**: `validar_sintaxis_cmd.py`, `qa_validar_cmd.py`, `transpilar_inverso_cmd.py`.
- **Scripts**: `targets_policy_common.py`, `audit_retired_targets.py`, `scripts/ci/validate_targets.py`, `scripts/ci/audit_targets_contract.py`, scripts de benchmarks.
- **Tests**: cobertura de transpilación inversa y contratos tier2 (ej.: `test_cli_transpilar_inverso_cmd.py`, `tests/integration/transpilers/test_official_backends_tier2.py`).

### `wasm`

- **Comandos**: `validar_sintaxis_cmd.py`, `qa_validar_cmd.py`.
- **Scripts**: `targets_policy_common.py`, `lint_legacy_aliases.py`, `scripts/ci/validate_workflow_target_matrix.py`, `scripts/ci/validate_targets.py`, scripts de benchmarks.
- **Tests**: cobertura de equivalencia de lenguaje y contratos de runtime (ej.: `test_cli_qa_validar_cmd.py`, `test_language_equivalence_contract.py`, `test_official_backends_contracts.py`).

### `asm`

- **Comandos**: `validar_sintaxis_cmd.py`, `qa_validar_cmd.py`.
- **Scripts**: `targets_policy_common.py`, `audit_retired_targets.py`, `scripts/ci/validate_targets.py`, `scripts/ci/audit_targets_contract.py`, scripts de benchmarks.
- **Tests**: cobertura de contrato/registro y choices legacy (ej.: `test_target_validation_contract.py`, `test_registry_contract_guardrail.py`, `test_compile_cmd_target_choices_aliases.py`).

## Fases por backend

Regla operativa común: **primero retirar exposición CLI y docs**, luego eliminar código muerto tras validación de no uso (telemetría + CI verde + inventario).

| Backend | Fase read-only | Fase disabled by default | Fase delete code |
|---|---|---|---|
| `asm` (`Q3 2026`) | Solo lectura y mantenimiento mínimo, sin features nuevas. | Bloqueado por defecto en CLI pública; habilitable solo en rutas internas controladas. | Al cierre de `Q3 2026`: eliminar transpiler/tests/hooks si no hay uso. |
| `go` (`Q4 2026`) | Congelar cambios funcionales; mantener únicamente compatibilidad de migración. | Deshabilitado por defecto fuera de modo legacy interno. | Al cierre de `Q4 2026`: eliminar `to_go.py`, tests y registros asociados sin tráfico. |
| `cpp` (`Q4 2026`) | Congelar cambios funcionales; soporte correctivo mínimo. | Deshabilitado por defecto fuera de modo legacy interno. | Al cierre de `Q4 2026`: eliminar `to_cpp.py`, tests y registros asociados sin tráfico. |
| `java` (`Q1 2027`) | Congelar cambios funcionales; foco en migración a `javascript`. | Deshabilitado por defecto fuera de modo legacy interno. | Al cierre de `Q1 2027`: eliminar `to_java.py`, tests y registros asociados sin tráfico. |
| `wasm` (`Q2 2027`) | Estado frozen/read-only (correcciones críticas únicamente). | Deshabilitado por defecto fuera de modo legacy interno. | Al cierre de `Q2 2027`: eliminar `to_wasm.py`, tests y registros asociados sin tráfico. |

## Secuencia obligatoria de ejecución

1. **Retiro de exposición CLI + docs**: comandos/flags legacy no visibles en superficie pública.
2. **Gating por defecto**: ejecución legacy bloqueada salvo modo interno temporal.
3. **Validación de no uso**: telemetría de uso legacy + inventario (`generate_internal_only_inventory.py`) + CI contract.
4. **Delete code**: eliminación física de transpilers/tests/hook internos por backend al vencer su ventana.
