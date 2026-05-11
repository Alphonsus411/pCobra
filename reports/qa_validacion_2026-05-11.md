# Validación solicitada (2026-05-11)

## Alcance
- Coberturas objetivo: `NodoLista`, `archivo.existe`, seguridad/sandbox y regresiones de módulos.
- Regresión de intérprete/REPL relevante.

## Comandos ejecutados
1. `pytest -q tests/unit/test_corelibs.py -k "archivo_existe or sandbox"`
2. `pytest -q tests/unit/test_transpiler_feature_parity.py -k "NodoLista"`
3. `pytest -q tests/unit/test_cli_entrypoint_imports.py tests/unit/test_interpreter_identifier_comparisons.py -k "regresion or regresión"`
4. `pytest -q tests/unit/test_cli_interactive_cmd.py -k "sandbox or repl"`
5. `PYTHONPATH=src pytest -q tests/test_cli_entrypoint_imports.py tests/unit/test_interpreter_identifier_comparisons.py -k "regresion or regresión"`
6. `PYTHONPATH=src pytest -q tests/unit/test_cli_interactive_cmd.py -k "repl or sandbox"`
7. `PYTHONPATH=src pytest -q tests/unit/test_transpiler_feature_parity.py -k "NodoLista"`
8. `PYTHONPATH=src pytest -q tests/unit/test_corelibs.py -k "archivo_existe_rechaza_fuera_del_sandbox"`

## Resultado resumido
- Los comandos de cobertura/regresión quedaron bloqueados por **errores de colección** del entorno/proyecto actual:
  - `ImportError: attempted relative import beyond top-level package` en tests que importan `core.interpreter`.
  - `ImportError` por importación circular parcial entre `pcobra.corelibs` y `pcobra.standard_library.asincrono`.
  - Ruta inexistente usada en un intento inicial: `tests/unit/test_cli_entrypoint_imports.py` (el archivo real está en `tests/test_cli_entrypoint_imports.py`).

## Verificaciones adicionales solicitadas
- No se introdujo sintaxis nueva (no se modificó código fuente del runtime/parser/lexer).
- No se relajó globalmente la sandbox.
- No se añadieron imports externos directos.

