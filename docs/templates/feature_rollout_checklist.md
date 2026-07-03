# Checklist de rollout de feature de lenguaje

Usa esta plantilla para cualquier feature nueva (`<feature_id>`).

## Identificador

- Feature ID: `<feature_id>`
- PR/RFC: `<enlace>`

## Resumen de archivos modificados

- `<ruta>`: `<motivo del cambio>`

## Resumen de pruebas añadidas

- `<ruta_test>`: `<caso cubierto>`
- Si no se añadieron pruebas, justificar por qué no aplica:

## Resultado de comandos ejecutados

- `<comando>`: `<resultado>`
- Indicar cualquier comando que no pudo ejecutarse y el motivo:

## POCs que deben repetirse manualmente

- `<POC/manual>`: `<pasos esperados>`
- Si no hay POCs manuales pendientes, indicar: `No aplica`.

## Confirmaciones explícitas de alcance

- [ ] No se tocó Lexer.
- [ ] No se tocó Parser.
- [ ] No se tocó gramática.
- [ ] No se tocaron tokens.
- [ ] No se tocaron nodos AST.
- [ ] No se tocaron transpiladores.
- [ ] No se cambió sintaxis Cobra.
- [ ] No se añadieron dependencias.

## Cobertura técnica

- [ ] gramática/parser/AST
  - Archivos tocados:
- [ ] intérprete
  - Archivos tocados:
- [ ] transpilers oficiales
  - Targets cubiertos: `python`, `javascript`, `rust`
- [ ] compat matrices
  - Matrices/documentos actualizados:
- [ ] tests unit/integration
  - Tests añadidos/actualizados:
- [ ] docs y ejemplos
  - Documentación:
  - Ejemplo mínimo en `examples/features/<feature_id>/minimal.co`:


## Selección de regresión por área

Marca los tests o jobs existentes que se ejecutaron para demostrar que el cambio no rompe cada área. Si un área no aplica al cambio, deja constancia explícita en la columna `Resultado / motivo`.

| Área | Pruebas o jobs existentes recomendados | Resultado / motivo |
| --- | --- | --- |
| Lexer | `pytest tests/test_lexer.py tests/test_lexer_parser_contract.py` | |
| Parser | `pytest tests/test_parser.py tests/test_lexer_parser_contract.py` | |
| AST | `pytest tests/test_parser.py tests/test_lexer_parser_contract.py tests/performance/test_transpile_time.py` | |
| Runtime | `pytest tests/cli/test_runtime_imports_contract.py tests/cli/test_repl_script_parity_contract.py tests/cli/test_repl_error_recovery_contract.py` | |
| Corelibs | `pytest tests/test_usar_public_exports_snapshot.py tests/cli/test_runtime_imports_contract.py` | |
| Transpiladores | `pytest tests/integration/transpilers/test_official_backends_tier2.py tests/integration/transpilers/test_decoradores_contract.py tests/performance/test_transpile_time.py` | |
| CobraHub | `pytest tests/cli/test_public_v2_commands_contract.py tests/cli/test_cli_alias_registration.py tests/cli/test_packaging_smoke.py` | |
| IDLE | `pytest tests/gui/test_app_import.py tests/gui/test_idle_packaging.py tests/gui/test_idle_path_guards.py tests/gui/test_runtime_file_helpers.py tests/gui/test_auto_suggestion_parser_contract.py` | |

- Si se toca un módulo compartido, añadir una prueba específica que confirme que el comportamiento previo sigue funcionando y enlazarla en `Resumen de pruebas añadidas`.
- No modificar gramática, tokens, nodos AST ni transpiladores salvo que una prueba específica falle y demuestre la necesidad; documentar esa prueba y la justificación en `Resultado de comandos ejecutados`.

## Validaciones manuales no ejecutadas

- `<validación>`: `<motivo>`
- Si todas las validaciones manuales aplicables se ejecutaron, indicar: `No aplica`.

## Verificación rápida

```bash
python scripts/ci/audit_feature_rollout.py --feature-id <feature_id>
```
