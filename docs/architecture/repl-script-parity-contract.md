# Contrato operativo de estabilización runtime (REPL ↔ Script)

## Objetivo

Definir y ejecutar un contrato operativo mínimo para evitar regresiones en la ruta de ejecución de CLI/REPL.

Este contrato se valida en CI con una batería cerrada que cubre 6 criterios:

1. CLI sin import errors.
2. Sin ciclos de import.
3. Comandos desacoplados.
4. Paridad REPL/script.
5. Persistencia de variables en loops.
6. Lexer/parser intactos.

## Criterios y mapeo a tests existentes

| Criterio | Tests concretos (ruta exacta) |
|---|---|
| CLI sin import errors | `tests/test_cli_entrypoint_imports.py` ; `tests/unit/test_cli_startup_import_contract.py` |
| Sin ciclos de import | `tests/unit/test_ci_check_import_cycles.py` |
| Comandos desacoplados | `tests/unit/test_ci_lint_no_cross_command_imports.py` ; `tests/unit/test_ci_lint_no_cross_command_imports_guard.py` ; `tests/unit/test_public_commands_no_direct_transpilers_contract.py` |
| Paridad REPL/script | `tests/unit/test_cli_execution_pipeline_contract.py::test_matriz_minima_paridad_execute_script_vs_repl` ; `tests/unit/test_cli_execution_pipeline_contract.py::test_contrato_resultado_igual_entre_modo_archivo_y_interactivo` ; `tests/unit/test_cli_execution_pipeline_contract.py::test_contrato_salida_y_error_iguales_entre_execute_e_interactive` |
| Persistencia de variables en loops | `tests/unit/test_cli_execution_pipeline_contract.py::test_paridad_repl_script_mientras_con_mutacion_persistente_mismo_entorno` ; `tests/unit/test_cli_execution_pipeline_contract.py::test_contrato_repl_igual_script_estado_final_con_bucles_y_asignaciones` ; `tests/unit/test_interpreter_loop_scope_regression.py` |
| Lexer/parser intactos | `tests/test_lexer.py` ; `tests/unit/test_lark_parser_tokens.py` ; `tests/unit/test_parser_error_reporting.py` |

## Batería contractual para CI (única fuente de ejecución)

La batería contractual se ejecuta de forma dedicada mediante un único comando `pytest` con rutas/nodos explícitos:

```bash
python -m pytest -q \
  tests/test_cli_entrypoint_imports.py \
  tests/unit/test_cli_startup_import_contract.py \
  tests/unit/test_ci_check_import_cycles.py \
  tests/unit/test_ci_lint_no_cross_command_imports.py \
  tests/unit/test_ci_lint_no_cross_command_imports_guard.py \
  tests/unit/test_public_commands_no_direct_transpilers_contract.py \
  tests/unit/test_cli_execution_pipeline_contract.py::test_matriz_minima_paridad_execute_script_vs_repl \
  tests/unit/test_cli_execution_pipeline_contract.py::test_contrato_resultado_igual_entre_modo_archivo_y_interactivo \
  tests/unit/test_cli_execution_pipeline_contract.py::test_contrato_salida_y_error_iguales_entre_execute_e_interactive \
  tests/unit/test_cli_execution_pipeline_contract.py::test_paridad_repl_script_mientras_con_mutacion_persistente_mismo_entorno \
  tests/unit/test_cli_execution_pipeline_contract.py::test_contrato_repl_igual_script_estado_final_con_bucles_y_asignaciones \
  tests/unit/test_interpreter_loop_scope_regression.py \
  tests/test_lexer.py \
  tests/unit/test_lark_parser_tokens.py \
  tests/unit/test_parser_error_reporting.py
```

## Regla de merge

El workflow dedicado `runtime-stabilization-contract` corre en `pull_request` y `push` a `main`.

Si cualquier test de esta batería falla, el job falla y el check de GitHub queda en rojo, bloqueando el merge cuando la rama protegida lo exige como required check.
