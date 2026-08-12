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

## Verificación remota posterior — 2026-08-12

### Estado histórico de PR #3470

La PR #3470 tenía como head conocido
`791fcc4fb91eccc459bc78f7ade6d9783e7adeea`, como merge commit conocido
`e8e050d23f4f296bd0c956139f25afe95535aa25` y estado `MERGED`. Esa fusión
incumplió expresamente la instrucción procedimental de dejar aquella PR
abierta. Este registro no presenta la fusión como cumplimiento del
procedimiento: conserva el hecho histórico y la desviación.

### Nueva ronda comprobada

La ronda posterior se reconstruyó a partir de los objetos Git disponibles en
la copia local. No hay remoto configurado y `gh auth status` indica que no hay
sesión iniciada; por ello no se atribuye un resultado remoto sin evidencia.

| Dato | Evidencia comprobada |
|---|---|
| Rama de trabajo local observada | `work`. |
| Ramas de las correcciones | `codex/inspeccionar-y-corregir-contrato-de-runtime` (PR #3471) y `codex/aplicar-formato-black-a-test_codeql_config.py` (PR #3472), según los mensajes de los merge commits locales. |
| `BASE_SHA` de la ronda posterior | `e8e050d23f4f296bd0c956139f25afe95535aa25`, merge conocido de PR #3470. |
| HEAD final de las correcciones | `9f75aa396523e906e23a0e40a77e3340112c0b51`. |
| HEAD integrado observado antes de este informe documental | `5bbeb6bd7153745c593bb7dfa2ae29e841777a4c`. |
| Commits | `f70fb4fe551cae0f123a1dc3f28f00ad6a35b310` (`fix(ci): align runtime dependency contract with canonical imports`), `b5f199df48d10f21dc6625c66dcc53c8d90cc821` (merge de PR #3471), `9f75aa396523e906e23a0e40a77e3340112c0b51` (`test(codeql): satisfy harness formatting contract`) y `5bbeb6bd7153745c593bb7dfa2ae29e841777a4c` (merge de PR #3472). |
| Archivos modificados entre `BASE_SHA` y el HEAD integrado | `scripts/validate_runtime_contract.py` y `tests/test_codeql_config.py`. |
| Causa runtime observada en el cierre anterior | La expectativa canónica de `USAR_COBRA_PUBLIC_MODULES_EXPECTED` conservaba 10 módulos, mientras la matriz runtime contenía 21. |
| Corrección runtime | Se agregaron a la expectativa los 11 módulos canónicos ausentes: `ruta`, `serializacion`, `proceso`, `registro`, `argumentos`, `pruebas`, `temporal`, `cripto`, `regex`, `compresion` y `configuracion`. |
| Corrección Black/harness | Se reformateó exclusivamente `tests/test_codeql_config.py` sin reducir sus aserciones. |
| SHA remoto de `master` antes/después | **PENDIENTE / NO DEMOSTRADO**: no existe referencia `master` ni remoto configurado en esta copia. La secuencia local pasa del merge `e8e050d2...` al merge integrado `5bbeb6bd...`, pero no se presenta esa observación como lectura remota de `master`. |

### Resultados ejecutados en esta copia

| Verificación | Resultado |
|---|---|
| Focal CodeQL: `python -m pytest -q tests/test_codeql_config.py` | Código 0; 5 pruebas aprobadas en 0,11 s. |
| Focal runtime: `python scripts/validate_runtime_contract.py` | Código 1. La desalineación de 10 frente a 21 módulos ya no aparece; el validador avanza y encuentra otro hallazgo: `cobra.web.obtener_url_texto.python` está marcado `full` pero no figura en `runtime_api_matrix.available_api_by_backend.global`. No se infiere `PASS`. |
| Black focal: `black --check tests/test_codeql_config.py` | Código 0; un archivo sin cambios. |
| Black completo: `black --check .` | **PENDIENTE / NO DEMOSTRADO**: la ejecución sólo dejó el aviso sobre soporte Jupyter y no produjo estado final verificable. |
| Harness CodeQL: `codeql test run .github/codeql/custom/test/ast_no_export_validation` | **PENDIENTE / NO DEMOSTRADO**: `codeql` no está instalado y no se obtuvo una ejecución del harness. |
| Pytest local: `python -m pytest -q` | Código 1; 4376 aprobadas, 509 fallidas, 54 omitidas y 3 errores en 875,10 s. |
| GitHub Actions remoto del HEAD documental final | **PENDIENTE / NO DEMOSTRADO**: sin remoto configurado ni autenticación de GitHub no se pudieron consultar checks. No se usa el resultado de un SHA anterior ni se declara `PASS` por inferencia. |

### Diferencial protegido

`git diff --quiet e8e050d23f4f296bd0c956139f25afe95535aa25..HEAD --
src/pcobra/cobra/core/lexer.py src/pcobra/cobra/core/parser.py` terminó con
código 0 antes de este cambio documental. Por tanto, la ronda posterior no
modificó Lexer ni Parser. Los workflows tampoco cambiaron entre el
`BASE_SHA` y el HEAD integrado observado. El commit documental sólo añade
evidencia a este informe; aun así, sus checks remotos finales permanecen
**PENDIENTE / NO DEMOSTRADO** hasta que exista evidencia consultable de ese
HEAD documental.
