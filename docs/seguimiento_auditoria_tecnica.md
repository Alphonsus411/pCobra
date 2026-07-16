# Seguimiento de auditoría técnica pCobra

Este documento resume el estado verificable de los hallazgos trabajados de forma incremental. Los estados permitidos son: `pendiente`, `en investigación`, `parcial`, `corregido`, `verificado` y `regresión`.

> Nota de alcance: este seguimiento no cambia la especificación del lenguaje, no modifica el libro normativo y no marca como completada una fase sin comandos reproducibles. El subcaso `validar-sintaxis` queda separado porque la arquitectura actual lo clasifica como ruta obsoleta/internal-migration-only y el libro normativo no lo exige como comando público.

## Estado por hallazgo

| Fase | Problema | Estado | Evidencia verificable | Observación |
|---|---:|---|---|---|
| Fase 0 | Línea base de Git, ramas, CLI/IDLE y suite contractual | verificado | `git status --short`; `git branch --show-current`; `git log -10 --oneline`; pruebas de ayuda CLI y suite razonable | La rama local activa es `work`; `origin/HEAD` no está configurado en el contenedor. |
| Fase 1 | 1 | verificado | `pytest -q tests/test_workflows_yaml.py` | Workflows críticos apuntan a `master` en lugar de `work`. |
| Fase 1 | 2 | verificado | `pytest -q tests/test_workflows_yaml.py` | `actionlint` se instala con versión/directorio explícitos y no con `-b` como versión. |
| Fase 1 | 3 | verificado | `pytest -q tests/test_tooling_excludes.py` | Black/Ruff/mypy/pytest evitan venvs, caches y `site-packages` versionados. |
| Fase 1 | 4 | verificado | `pytest -q tests/test_codeql_config.py` | CodeQL usa rutas existentes y queries resolubles desde la raíz del repositorio. |
| Fase 2 | 5 | verificado | `pytest -q tests/integration/test_usar_core_contract_full.py` | `usar` mantiene bloqueo de módulos externos y corrige la confusión entre raíz de proyecto/runner. |
| Fase 2 | 6 | verificado | `pytest -q tests/integration/test_run_repl_equivalence.py tests/integration/test_usar_project_modules.py` | El intérprete inicializa estado de imports y cachea rutas importadas. |
| Fase 2 | 7 | verificado | `pytest -q tests/integration/test_usar_project_modules.py tests/unit/test_project_root_usar_resolution.py` | Detección de ciclos de importación sin tocar sintaxis de `usar`. |
| Fase 3 | 8 | verificado | `pytest -q tests/unit/test_resource_limits_run_service.py` | Los bucles/ejecuciones largas quedan cubiertos por timeout e aislamiento de proceso. |
| Fase 3 | 9 | verificado | `pytest -q tests/unit/test_resource_limits_run_service.py` | `cobra run --sandbox` ya no falla por `main_file` inesperado. |
| Fase 3 | 10 | verificado | `pytest -q tests/unit/test_resource_limits_run_service.py tests/core/test_resource_limits.py` | Los límites se aplican en proceso aislado y no contaminan el anfitrión. |
| Fase 4 | 11 | verificado | `pytest -q tests/integration/test_run_repl_equivalence.py tests/gui/test_gui_runtime_execution_scope.py` | CLI/REPL/IDLE mantienen coherencia para imports, errores y runtime evaluado. |
| Fase 4 | 12 | verificado | `pytest -q tests/unit/test_backend_public_contract.py tests/unit/test_architecture_overview.py` | `INTERNAL_BACKENDS` queda definido y separado de backends públicos. |
| Fase 4 | 13 | verificado | `pytest -q tests/unit/test_backend_pipeline_runtime_manager.py` | `build` rechaza AST semánticamente inválido antes de transpilar. |
| Fase 5 | 14 | parcial | `python -m pcobra gui --help`; `pytest -q tests/unit/test_cli_gui.py tests/integration/test_cli_public_help_contract.py` | `cobra gui` está corregido/verificado. `validar-sintaxis` queda pendiente de decisión: no es público según arquitectura actual. |
| Fase 5 | 15 | verificado | `pytest -q tests/unit/test_transpile_python.py::test_transpile_async_top_level_esperar_uses_asyncio_run tests/integration/test_transpilador_syntax.py::test_transpilador_syntax[python]`; `python -m py_compile tests/data/expected_examples/async_await.py` | El backend Python emite `asyncio.run(...)` para `esperar` a nivel de módulo. |
| Fase 6 | 2 | verificado | `pytest -q tests/unit/test_plan_regresion_fases.py`; `! rg -n "cargo test\|cargo insta\|make ci\|scripts/ci/run_all\\.sh" docs/plan_regresion_fases.md` | `docs/plan_regresion_fases.md` usa comandos Python/pytest reales. |

## Pendientes explícitos

| Ítem | Estado | Siguiente acción |
|---|---|---|
| `validar-sintaxis` como comando público | pendiente | Solicitar decisión de mantenedor: recuperarlo públicamente, mantenerlo legacy/internal-only o actualizar documentación secundaria. |
| Suite completa `pytest -q` | en investigación | Persisten fallos preexistentes/infraestructura en CLI legacy: falta ejecutable `cobra` en PATH y comandos legacy `python -m cli.cli ejecutar/jupyter/docs` reciben ayuda pública v2. |
| Cierre documental final de Fase 6 | pendiente | Completar seguimiento sólo con comandos y resultados reproducibles por cada fase. |

## Confirmación de alcance

- Lexer, Parser y gramática no se modificaron para estos hallazgos.
- No se añadió sintaxis Cobra nueva.
- Las correcciones de runtime/transpilación se hicieron en servicios, sandbox, intérprete, loader, build pipeline o documentación de seguimiento.
