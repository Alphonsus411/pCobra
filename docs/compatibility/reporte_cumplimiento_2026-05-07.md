# Reporte de cumplimiento — 2026-05-07

## Alcance
Verificación de criterios solicitados sobre estabilidad de Lexer/Parser, superficie pública, política `usar`, encapsulamiento de backends/SDKs y compatibilidad de contrato CLI/BackendPipeline/RuntimeManager.

## Resultado por criterio

1. **Lexer y Parser sin cambios**
   - `git diff -- src/pcobra/cobra/core/lexer.py src/pcobra/cobra/core/parser.py` no reporta diferencias.
   - **Estado:** ✅ Cumple.

2. **Sin nuevos puntos de entrada públicos con nombres backend**
   - Revisión focalizada de superficie pública (`cobra/cli`, `src/pcobra/cobra/__init__.py`, `src/pcobra/cobra/bindings/*`, `src/pcobra/cobra/usar_loader.py`).
   - Solo aparecen referencias de resguardo/política (bloqueo), no como nuevo entrypoint público.
   - **Estado:** ✅ Cumple.

3. **Módulos `usar` Cobra-facing y canónicos en español**
   - `usar_loader.py` fuerza identificadores simples, bloquea hints internos (`pcobra`, `backend`, `transpiler`, etc.) y exige allowlist canónica.
   - Se rechazan explícitamente módulos no canónicos (`numpy`, `node-fetch`, `serde`, `holobit_sdk`).
   - Suite de contrato `usar` ejecutada en verde.
   - **Estado:** ✅ Cumple.

4. **Encapsulamiento de SDKs/backends como detalle interno**
   - Contratos/lints asociados pasaron (`test_backend_public_contract`, `test_ci_lint_public_commands_internal_backends`).
   - **Estado:** ✅ Cumple.

5. **Compatibilidad CLI contract, BackendPipeline y RuntimeManager**
   - `test_backend_pipeline_runtime_manager.py` pasa.
   - Se detecta regresión existente en `test_cli_execution_pipeline_contract.py` (paridad ExecuteCommand vs REPL) con 5 fallos.
   - **Estado:** ⚠️ Cumplimiento parcial (BackendPipeline/RuntimeManager OK; paridad CLI Execute/REPL con divergencias activas).

## Evidencia de ejecución
- `pytest -q tests/unit/test_backend_pipeline_runtime_manager.py tests/unit/test_backend_public_contract.py tests/unit/test_usar_public_contract.py tests/unit/test_usar_policy_contract.py tests/unit/test_ci_lint_public_commands_internal_backends.py` → **21 passed**.
- `pytest -q tests/unit/test_backend_pipeline_runtime_manager.py tests/unit/test_cli_execution_pipeline_contract.py tests/unit/test_backend_public_contract.py tests/unit/test_usar_public_contract.py tests/unit/test_usar_policy_contract.py tests/unit/test_ci_lint_public_commands_internal_backends.py` → **5 failed / 6 passed** en `test_cli_execution_pipeline_contract.py`.

## Conclusión
Se cumple de forma satisfactoria 1, 2, 3 y 4. El criterio 5 presenta una incompatibilidad puntual y reproducible en el contrato de paridad entre ejecución script y REPL del CLI.
