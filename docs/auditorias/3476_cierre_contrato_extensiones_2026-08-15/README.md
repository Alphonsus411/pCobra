# Cierre de `contrato-extensiones` (2026-08-15)

## Identidad y alcance

| Dato | Valor comprobado |
|---|---|
| Fecha | `2026-08-15` |
| Rama de cierre | `fix/contrato-extensiones-cobra` |
| `BASE_SHA` | `1cb9c6d1f195738cdeffe618dafa9aa3cc819504` |
| HEAD inicial | `6fcc4f701782a2481c8dbba7bce87e8812982b4f` |
| Commit Runtime Contract | `d2f6e2a91a1aa6e0f4687e07f612b6fc8c656df0` |
| Commit CodeQL | `ae4976f75140dd07945189b07d5f202fcdb41a4c` |

`BASE_SHA` es el merge inmediatamente anterior a las dos correcciones que se
cierran. El primer comando de identidad imprimió por error como `BASE_SHA` el
padre de ese merge (`5bbeb6bd7153745c593bb7dfa2ae29e841777a4c`);
esta discrepancia queda declarada y todas las comparaciones de cierre usan de
forma explícita el valor normativo de la tabla.

## Runtime Contract

### Causa raíz y corrección

El contrato declaraba `cobra.web.obtener_url_texto.python` con soporte `full`,
pero el símbolo faltaba en la superficie Python global y de `corelibs` de la
matriz generada y en el snapshot de paridad. El commit Runtime añadió
exclusivamente esa entrada a
`src/pcobra/cobra/transpilers/runtime_api_parity_snapshot.json` y regeneró
`docs/_generated/runtime_api_matrix.json` y
`docs/_generated/runtime_api_matrix.md`.

La corrección es incremental: al volver a ejecutar el validador, el hallazgo
de `obtener_url_texto` desaparece y queda expuesto otro incumplimiento,
`cobra.system.ejecutar_comando_async.python`. Una ejecución detached del
`BASE_SHA` confirma que allí el primer error era `obtener_url_texto`; por ello
el error ahora visible se clasifica como **preexistente y antes oculto por el
fail-fast**, no como regresión de estos cuatro cambios. El cierre global del
Runtime Contract queda **PENDIENTE / NO DEMOSTRADO** y no se declara PASS.

### Evidencia focal de Runtime

| Comando exacto | Resultado exacto |
|---|---|
| `python scripts/validate_runtime_contract.py` | Código 1; `ContractValidationError: cobra.system.ejecutar_comando_async.python: marcado full pero no aparece en runtime_api_matrix.available_api_by_backend.global`. **PENDIENTE / NO DEMOSTRADO**. |
| `python -m pytest -q tests/unit/test_runtime_api_matrix_contract.py tests/integration/test_repl_usar_entrypoints_contract.py` | Código 1; **2 failed, 96 passed, 2 warnings in 3.21s**. Los dos fallos focales informan 13 símbolos Python nuevos sin mapear (`contiene`, `ejecutar_proceso`, `falso`, `igual`, `info_registro`, `lanza_error`, `leer_configuracion`, `leer_ini`, `leer_json_serializacion`, `leer_toml`, `toml_disponible`, `unir_ruta`, `verdadero`); son deuda preexistente fuera de la corrección incremental de `obtener_url_texto`. **PENDIENTE / NO DEMOSTRADO**. |
| `tmp=$(mktemp -d /tmp/pcobra-base.XXXXXX); git worktree add --detach "$tmp" 1cb9c6d1f195738cdeffe618dafa9aa3cc819504 >/tmp/worktree-add.log && (cd "$tmp" && PYTHONPATH=src python scripts/validate_runtime_contract.py); rc=$?; echo EXIT_CODE=$rc; git worktree remove --force "$tmp"; cat /tmp/worktree-add.log` | Código 0 del wrapper; el validador detached terminó con código interno 1 y `cobra.web.obtener_url_texto.python: marcado full pero no aparece...`; la limpieza del worktree terminó correctamente. |
| `tmp=$(mktemp -d /tmp/pcobra-base.XXXXXX); git worktree add --detach "$tmp" 1cb9c6d1f195738cdeffe618dafa9aa3cc819504 >/tmp/worktree-add.log && (cd "$tmp" && PYTHONPATH=src /workspace/pCobra/.venv/bin/python scripts/validate_runtime_contract.py); rc=$?; echo EXIT_CODE=$rc; git worktree remove --force "$tmp"; cat /tmp/worktree-add.log` | Código 0 del wrapper, pero ejecución interna 127 porque no existe `/workspace/pCobra/.venv/bin/python`; evidencia ambiental inválida, repetida correctamente con `python` en el comando anterior. |

## Integridad de Lexer, Parser y snapshots canónicos

Los cuatro hashes iniciales coinciden exactamente con los blobs del snapshot
canónico detached `f92f5f5863ef51d9722cdaea7a1c42619135e9a8`:

| Archivo protegido | Hash inicial | Hash canónico |
|---|---|---|
| `src/pcobra/cobra/core/lexer.py` | `50dbd208b1ff09c80462bca4036a8dcc84649be8` | `50dbd208b1ff09c80462bca4036a8dcc84649be8` |
| `src/pcobra/cobra/core/parser.py` | `cdcb0230e5ea4ea47ae710cbaccb38afde5b87d0` | `cdcb0230e5ea4ea47ae710cbaccb38afde5b87d0` |
| `src/pcobra/core/lexer.py` | `413cd9cdbf3835657cc766e645b1472bee11886c` | `413cd9cdbf3835657cc766e645b1472bee11886c` |
| `src/pcobra/core/parser.py` | `aad60be7f3f3e029c452937edf3c2e4656c59459` | `aad60be7f3f3e029c452937edf3c2e4656c59459` |

El comando explícito
`git diff --name-status 1cb9c6d1f195738cdeffe618dafa9aa3cc819504..HEAD -- src/pcobra/cobra/core/lexer.py src/pcobra/cobra/core/parser.py src/pcobra/core/lexer.py src/pcobra/core/parser.py`
no produjo salida. No fue necesaria ninguna restauración: las dos copias de
Lexer y Parser mantienen identidad byte a byte con sus snapshots canónicos.

## CodeQL

### Causa raíz y corrección

El workflow suponía que `codeql` quedaba disponible por nombre en `PATH`
después de `github/codeql-action/init`. Esa suposición no forma parte del
contrato del action y el paso de queries no encontraba el ejecutable. La
corrección asignó `id: codeql-init` al paso de inicialización e invoca de forma
explícita `"${{ steps.codeql-init.outputs.codeql-path }}" test run ...`.

| Comando exacto | Resultado exacto |
|---|---|
| `python -m pytest -q tests/test_codeql_config.py tests/test_workflows_yaml.py` | Código 0; **27 passed in 0.08s**. |
| `command -v codeql` | Código 1 y salida vacía. |
| `codeql test run .github/codeql/custom/test/ast_no_export_validation` | **PENDIENTE / NO DEMOSTRADO**: no se ejecutó porque `command -v codeql` confirmó que el CLI no está disponible en esta copia. No se infiere PASS del contrato textual. |

## Inventario diferencial y exclusiones confirmadas

Entre `BASE_SHA` y el HEAD inicial sólo cambiaron estos archivos:

```text
M  .github/workflows/codeql.yml
M  docs/_generated/runtime_api_matrix.json
M  docs/_generated/runtime_api_matrix.md
M  src/pcobra/cobra/transpilers/runtime_api_parity_snapshot.json
```

Después se añadió únicamente este informe. La revisión manual del diff
completo confirma que no se modificaron:

- ambas copias de Lexer y Parser:
  `src/pcobra/cobra/core/{lexer,parser}.py` y
  `src/pcobra/core/{lexer,parser}.py`;
- sus cuatro blobs/snapshots canónicos en `f92f5f58...`;
- AST (`src/pcobra/core/ast_nodes.py`) ni gramática
  (`docs/gramatica.ebnf`);
- `src/pcobra/corelibs/red.py` ni
  `src/pcobra/standard_library/red.py`;
- sandbox, red, filesystem, procesos, ZIP ni validadores de seguridad;
- la query `.github/codeql/custom/ast-no-export-validation.ql` ni ninguno
  de sus fixtures bajo
  `.github/codeql/custom/test/ast_no_export_validation/`.

Estas afirmaciones proceden del diferencial por nombres y de la inspección
del parche, no de inferencias sobre el contenido de las pruebas.

## Verificaciones de cierre

| Comando exacto | Resultado exacto |
|---|---|
| `git status --short --branch` (inicial) | Código 0; `## fix/contrato-extensiones-cobra`, árbol limpio. |
| `git diff --stat 1cb9c6d1f195738cdeffe618dafa9aa3cc819504..HEAD` (antes del informe) | Código 0; 4 archivos, 8 inserciones y 2 eliminaciones. |
| `git diff --name-status 1cb9c6d1f195738cdeffe618dafa9aa3cc819504..HEAD` (antes del informe) | Código 0; los cuatro archivos enumerados arriba. |
| `git diff --check` | Código 0, sin salida. |
| `black --check .` | Código 0; aviso de que se omiten notebooks porque no están instaladas las dependencias Jupyter; `1159 files would be left unchanged`. No se reformateó ningún archivo. |
| `python -m pytest -q` | Código 1; **505 failed, 4380 passed, 54 skipped, 31 warnings, 3 errors in 542.91s (0:09:02)**. Los 2 fallos de `test_runtime_api_matrix_contract.py` son deuda focal preexistente descrita arriba; el resto coincide en clase con la suite roja preexistente documentada (incluidos 3 errores SQLite de `test_token_cache.py`) y se clasifica como preexistente/ambiental, no nuevo por el diff de cuatro archivos. No se intentó corregir nada fuera de alcance y el resultado queda **PENDIENTE / NO DEMOSTRADO**. |

La primera ejecución agrupada de verificaciones quedó interrumpida durante
`black --check .` sin código final verificable. Se clasificó como
**PENDIENTE / NO DEMOSTRADO** y se repitieron individualmente Black, el
validador y ambos grupos focales; la tabla sólo atribuye resultados a esas
repeticiones terminadas.

## Hashes finales y conclusión

| Archivo protegido | Hash final | Comparación |
|---|---|---|
| `src/pcobra/cobra/core/lexer.py` | `50dbd208b1ff09c80462bca4036a8dcc84649be8` | Idéntico al inicial y canónico. |
| `src/pcobra/cobra/core/parser.py` | `cdcb0230e5ea4ea47ae710cbaccb38afde5b87d0` | Idéntico al inicial y canónico. |
| `src/pcobra/core/lexer.py` | `413cd9cdbf3835657cc766e645b1472bee11886c` | Idéntico al inicial y canónico. |
| `src/pcobra/core/parser.py` | `aad60be7f3f3e029c452937edf3c2e4656c59459` | Idéntico al inicial y canónico. |

Los cambios funcionales permanecen separados en el commit Runtime
`d2f6e2a9...` y el commit CodeQL `ae4976f7...`; este cierre conserva además
dos commits documentales mínimos, uno por bloqueo. La configuración textual
de CodeQL y sus pruebas locales pasan. El harness real de CodeQL y el Runtime
Contract completo permanecen **PENDIENTE / NO DEMOSTRADO** por las
limitaciones y fallos explícitos anteriores.
