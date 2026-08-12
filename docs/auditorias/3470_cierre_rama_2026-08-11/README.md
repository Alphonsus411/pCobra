# Cierre de rama e integridad (2026-08-11)

## Identidad e inventario inicial

La revisión comenzó con el árbol limpio en la rama `work`. Se fijó
`BASE_SHA=6ee8befecf862923ed8321d5692a4d06bed01d7b` antes de introducir este
informe documental.

El inventario inicial de rutas relacionadas por nombre con gramática, tokens o
precedencia fue:

```text
docs/gramatica.ebnf
scripts/grammar_coverage.py
src/pcobra/core/token_contract.py
tests/unit/test_lark_parser_missing_grammar.py
tests/unit/test_lark_parser_tokens.py
tests/unit/test_lexer_token_index.py
tests/unit/test_nuevos_tokens.py
tests/unit/test_token_cache.py
```

## Archivos protegidos

Los resultados de `git hash-object` registrados antes del primer cambio y los
obtenidos al repetir el comando fueron idénticos:

| Archivo | Hash Git inicial y final |
|---|---|
| `src/pcobra/cobra/core/lexer.py` | `50dbd208b1ff09c80462bca4036a8dcc84649be8` |
| `src/pcobra/cobra/core/parser.py` | `cdcb0230e5ea4ea47ae710cbaccb38afde5b87d0` |
| `src/pcobra/core/ast_nodes.py` | `d7792bc949f3ad667480a30922c96e84da559bab` |
| `src/pcobra/core/optimizations/constant_folder.py` | `49289be11343bb1cfae77bd18ae44d707601a1a2` |

Tanto el diferencial explícito de esas cuatro rutas como
`git diff --name-only "$BASE_SHA"..HEAD -- src/pcobra` quedaron vacíos. El
único archivo del diferencial final es este informe. La comparación de ese
nombre con el inventario inicial y con los términos `grammar`, `gramatica`,
`token` y `precedence` no produjo coincidencias. La revisión manual confirma
que no se modificaron Lexer, Parser, AST, optimización constante, gramática,
tokens ni precedencia.

## Verificaciones finales

| Comando | Resultado |
|---|---|
| `git status` | Código 0; árbol limpio antes de crear este informe. |
| `git diff --check` | Código 0. |
| `python -m compileall src` | Código 0. |
| `ruff check .` | Código 0; `All checks passed!`. |
| `black --check .` | Código 1; reformatearía `tests/test_codeql_config.py` y dejaría 1158 archivos sin cambios. |
| `python -m pytest --collect-only -q` | Código 0; 4939 pruebas recolectadas y tres advertencias. |
| `python -m pytest -q` | Código 1; 4377 aprobadas, 508 fallidas, 54 omitidas y 3 errores en 847,14 s. |

No se modificó el archivo señalado por Black porque pertenece al baseline y
la orden de cierre prohíbe reescribir cambios previos.

## Comandos exactos de workflows

### Lint

Se ejecutaron, en el orden del workflow, `black --check .` y los diez comandos
Python posteriores. Black falló como se consigna arriba. Pasaron los nueve
gates intermedios; `python scripts/validate_runtime_contract.py` falló con
`RuntimeError: Contrato usar canónico desalineado`: la matriz actual contiene
21 módulos y la expectativa conserva 10. Por tanto Lint permanece rojo.

### CodeQL tests

`codeql test run .github/codeql/custom/test/ast_no_export_validation` terminó
con código 127 porque el ejecutable `codeql` no está instalado. Es una
limitación del entorno, no un resultado verde.

### Compatibility

El comando bloqueante exacto con sus cinco archivos obtuvo 128 pruebas
aprobadas. `python scripts/ci/validate_library_compatibility_matrix.py` también
terminó con código 0.

### Tests

El comando focal exacto de cuatro archivos del paso `Run tests` obtuvo 99
pruebas aprobadas. La suite general falló con 508 pruebas fallidas y 3 errores,
como se consigna en la tabla anterior; no se ocultan esos resultados rojos del
baseline.
