# Adenda de cierre Runtime Contract y Full CodeQL (2026-08-16 UTC)

## Identidad y alcance

| Dato | Valor real observado |
|---|---|
| `BASE_SHA` | `874a54603d4e53c1bdf1edf66efbb6aa5edd669c` |
| `HEAD_SHA` funcional final auditado | `183b67b84b240b311b0fdf7557d1673accd4df93` |
| Rama de entrega | `fix/contrato-extensiones-cobra` |
| Rama al inicio | `work` |
| `master` antes / después | `NOT DEMONSTRATED`: la referencia local no existe |
| `origin/master` antes / después | `NOT DEMONSTRATED`: no hay remoto ni referencia remota |

El `HEAD_SHA` identifica exactamente el árbol funcional sobre el que se ejecutaron
Runtime Contract y Full CodeQL. El commit único posterior sólo incorpora esta
adenda: un commit no puede contener su propio SHA sin alterar recursivamente ese
mismo SHA.

Errores literales al resolver las referencias solicitadas:

```text
fatal: ambiguous argument 'master': unknown revision or path not in the working tree.
Use '--' to separate paths from revisions, like this:
'git <command> [<revision>...] -- [<file>...]'
fatal: ambiguous argument 'origin/master': unknown revision or path not in the working tree.
Use '--' to separate paths from revisions, like this:
'git <command> [<revision>...] -- [<file>...]'
```

No se hizo merge ni checkout a `master`, y esta adenda no modifica ni elimina
ninguna auditoría anterior.

## Archivos modificados

La lista exacta del commit focal es:

```text
docs/auditorias/3493_adenda_cierre_runtime_codeql_2026-08-16/README.md
```

Lexer, Parser, Runtime, queries y configuración CodeQL permanecieron sin cambios.

La lista exacta acumulada de `BASE_SHA..HEAD` (incluye cambios que ya estaban
integrados antes de abrir esta rama documental) es:

```text
.github/codeql/custom/missing-codegen-exception.ql
.github/codeql/custom/unsafe-eval-exec.ql
docs/_generated/runtime_api_matrix.json
docs/_generated/runtime_api_matrix.md
docs/auditorias/3492_full_codeql_2026-08-16/README.md
docs/auditorias/3493_adenda_cierre_runtime_codeql_2026-08-16/README.md
src/pcobra/cobra/transpilers/runtime_api_parity_snapshot.json
tests/test_codeql_config.py
```

## Artefactos Runtime generados

Después de ejecutar `python scripts/generar_matriz_api_runtime.py`, tanto
`git status --short` como los diffs quedaron vacíos. El resumen exacto para
`docs/_generated/runtime_api_matrix.json` y
`docs/_generated/runtime_api_matrix.md` es **0 archivos, 0 inserciones y 0
borrados**; el diff completo también es vacío. Por tanto, los artefactos Runtime
coinciden byte a byte con la salida del generador y no tienen modificaciones
manuales en el commit focal.

Respecto de `BASE_SHA`, el diff resumido acumulado es: JSON `118` inserciones y
`0` borrados; Markdown `5` inserciones y `5` borrados; total de ambos: `123`
inserciones y `5` borrados. Esos cambios preceden esta adenda y la regeneración
demostró que son reproducibles, no ediciones manuales.

## Blockers cerrados y nuevos

- **Runtime: RESUELTO / PASS.** Las 9 pruebas dirigidas pasan, la matriz se
  regenera sin deriva y `validate_runtime_contract.py` informa literalmente
  `✅ Runtime contract validation: OK`.
- **CodeQL: RESUELTO / PASS local.** Las queries dirigidas compilan, los cuatro
  harnesses pasan y el análisis completo configurado termina con exit 0.
- **Blocker nuevo independiente (publicación del PR):** el entorno no expone
  `make_pr`, no tiene remoto configurado y `gh pr create` terminó con exit 4:
  `To get started with GitHub CLI, please run:  gh auth login` y
  `Alternatively, populate the GH_TOKEN environment variable with a GitHub API
  authentication token.` Este bloqueo no afecta los PASS locales, pero impide
  demostrar CI remoto y materializar el PR desde esta copia.
- **Advertencias no bloqueantes:**
  `WARNING: QLDoc comment is not attached to any QL element
  (/workspace/pCobra/.github/codeql/custom/unsafe-eval-exec.ql:11,1-13,4)` y,
  durante la autodetección del extractor,
  `[build-stderr] /bin/sh: 1: python2: not found`. CodeQL continuó con Python
  3.12.13 y terminó correctamente.

## Evidencia CodeQL 2.26.3

El bundle oficial se descargó fuera del repositorio en `/tmp`. `codeql version`
informó `CodeQL command-line toolchain release 2.26.3` y `Unpacked in:
/tmp/codeql-bundle-2.26.3/codeql`.

- `query compile` de `unsafe-eval-exec.ql`: PASS, exit 0 (con la advertencia
  QLDoc anterior).
- `query compile` de `missing-codegen-exception.ql`: PASS, exit 0.
- `test run` de ambos directorios configurados en CI: `All 4 tests passed`, exit
  0.
- `database create`: PASS, 1.382 módulos procesados, base finalizada en
  `/tmp/pcobra-codeql-db-final`, exit 0.
- `database analyze`: PASS, 49/49 queries evaluadas, resultados interpretados,
  1.166/1.166 archivos Python y 16/16 archivos GitHub Actions escaneados, exit 0.
- SARIF: `/tmp/pcobra-codeql-final.sarif`, 923.842 bytes, 1 run y 96 resultados.

**CI remoto: NOT DEMONSTRATED.** `git remote -v` no produjo salida; sin remoto ni
credenciales/contexto de repositorio no se puede publicar ni consultar una
corrida asociada al SHA final. El PASS local no se presenta como sustituto de
esa evidencia remota.

## Integridad Lexer/Parser

Los hashes `git hash-object` antes y después son idénticos y coinciden con los
valores exigidos:

| Archivo | Antes | Después |
|---|---|---|
| `src/pcobra/cobra/core/lexer.py` | `50dbd208b1ff09c80462bca4036a8dcc84649be8` | `50dbd208b1ff09c80462bca4036a8dcc84649be8` |
| `src/pcobra/cobra/core/parser.py` | `cdcb0230e5ea4ea47ae710cbaccb38afde5b87d0` | `cdcb0230e5ea4ea47ae710cbaccb38afde5b87d0` |
| `src/pcobra/core/lexer.py` | `413cd9cdbf3835657cc766e645b1472bee11886c` | `413cd9cdbf3835657cc766e645b1472bee11886c` |
| `src/pcobra/core/parser.py` | `aad60be7f3f3e029c452937edf3c2e4656c59459` | `aad60be7f3f3e029c452937edf3c2e4656c59459` |

## Registro de comandos

Todos los comandos ejecutados durante esta ronda, incluidos los de inspección,
se recogen a continuación. `PASS` significa exit 0; los fallos esperados al
consultar refs inexistentes se clasifican `NOT DEMONSTRATED`, no como fallos del
producto.

| Comando | Exit | Resultado |
|---|---:|---|
| `pwd` | 0 | PASS: `/workspace/pCobra` |
| `find .. -name AGENTS.md -print` | 0 | PASS: sólo `../pCobra/AGENTS.md` |
| `cat AGENTS.md` | 0 | PASS |
| `git status --short --branch` | 0 | PASS: limpio, rama `work` |
| `git branch --show-current` | 0 | PASS: `work` |
| `git rev-parse HEAD` | 0 | PASS: `183b67b84b240b311b0fdf7557d1673accd4df93` |
| `git rev-parse master` | 128 | NOT DEMONSTRATED: error literal documentado arriba |
| `git rev-parse origin/master` | 128 | NOT DEMONSTRATED: error literal documentado arriba |
| `git log -1 --oneline` | 0 | PASS |
| `git show-ref --heads --remotes` | 129 | NOT DEMONSTRATED: opción `--remotes` no soportada; se ejecutó fallback |
| `git show-ref` | 0 | PASS: sólo `refs/heads/work` inicialmente |
| `git remote -v` | 0 | NOT DEMONSTRATED: salida vacía |
| `git cat-file -t 874a54603d4e53c1bdf1edf66efbb6aa5edd669c` | 0 | PASS: `commit` |
| `git merge-base --is-ancestor 874a54603d4e53c1bdf1edf66efbb6aa5edd669c HEAD` | 0 | PASS |
| `git hash-object` sobre los cuatro archivos protegidos | 0 | PASS: valores de la tabla |
| `find scripts tests .github -maxdepth 4 -type f ...` | 0 | PASS: inventario Runtime/CodeQL |
| `command -v codeql` | 1 | NOT DEMONSTRATED: no estaba en `PATH` |
| `codeql version` | 127 | NOT DEMONSTRATED: `codeql: command not found` |
| `command -v make_pr` | 1 | NOT DEMONSTRATED: helper no instalado |
| `command -v gh` | 0 | PASS |
| `find /workspace /opt /root -maxdepth 5 -type f -name codeql ...` | 0 | NOT DEMONSTRATED: sin binario |
| inspecciones `find`, `sed`, `git log`, `git show` y `rg` de configuración/auditorías | 0 | PASS |
| `git switch -c fix/contrato-extensiones-cobra` | 0 | PASS |
| `git diff --check` (inicial) | 0 | PASS |
| `black --check tests/test_codeql_config.py` | 0 | PASS: 1 archivo sin cambios |
| `python -m pytest -q tests/cli/test_runtime_imports_contract.py tests/unit/test_runtime_api_matrix_contract.py` | 0 | PASS: 9 passed |
| `python scripts/generar_matriz_api_runtime.py` | 0 | PASS |
| `python scripts/validate_runtime_contract.py` | 0 | PASS |
| `python -m pytest -q tests/test_codeql_config.py` | 0 | PASS: 9 passed |
| `git status --short` tras generar | 0 | PASS: vacío |
| `git diff --stat -- docs/_generated/runtime_api_matrix.json docs/_generated/runtime_api_matrix.md` | 0 | PASS: vacío |
| `git diff -- docs/_generated/runtime_api_matrix.json docs/_generated/runtime_api_matrix.md` | 0 | PASS: vacío |
| `curl -fL --retry 3 --output /tmp/codeql-bundle-2.26.3/codeql-bundle-linux64.tar.gz https://github.com/github/codeql-action/releases/download/codeql-bundle-v2.26.3/codeql-bundle-linux64.tar.gz` | 0 | PASS: bundle oficial descargado |
| `tar -xzf ... -C /tmp/codeql-bundle-2.26.3` | 0 | PASS |
| `/tmp/codeql-bundle-2.26.3/codeql/codeql version` | 0 | PASS: 2.26.3 |
| `/tmp/codeql-bundle-2.26.3/codeql/codeql query compile .github/codeql/custom/unsafe-eval-exec.ql` | 0 | PASS con warning QLDoc |
| `/tmp/codeql-bundle-2.26.3/codeql/codeql query compile .github/codeql/custom/missing-codegen-exception.ql` | 0 | PASS |
| `/tmp/codeql-bundle-2.26.3/codeql/codeql test run .github/codeql/custom/test/ast_no_export_validation .github/codeql/custom/test/ast_no_type_validation` | 0 | PASS: 4/4 |
| `/tmp/codeql-bundle-2.26.3/codeql/codeql database create /tmp/pcobra-codeql-db-final --language=python --build-mode=none --source-root=/workspace/pCobra --codescanning-config=.github/codeql/custom/codeql-config.yml` | 0 | PASS |
| `/tmp/codeql-bundle-2.26.3/codeql/codeql database analyze /tmp/pcobra-codeql-db-final --format=sarif-latest --output=/tmp/pcobra-codeql-final.sarif --sarif-category=python --threads=0` | 0 | PASS |
| script Python de lectura y recuento del SARIF | 0 | PASS: 1 run, 96 resultados, 923.842 bytes |
| `git diff --check` (final) | 0 | PASS |
| repetición final de `black`, pruebas Runtime, generador, validador y pruebas CodeQL | 0 | PASS |
| `git rev-parse master` / `git rev-parse origin/master` (final) | 128 / 128 | NOT DEMONSTRATED: refs inexistentes |
| `git diff --exit-code -- docs/_generated/runtime_api_matrix.json docs/_generated/runtime_api_matrix.md` | 0 | PASS: sin modificación manual |
| `git diff --check --cached` | 0 | PASS |
| `git diff --stat --cached`, `git diff --name-only --cached` y `git diff --cached` | 0 | PASS: un único archivo documental revisado íntegramente |
| `git commit -m "docs(audit): add Runtime and CodeQL closure addendum"` | 0 | PASS: commit focal único (posteriormente enmendado sólo para registrar el blocker de publicación) |
| inventario de herramientas PR (`ALL_TOOLS`) | 0 | NOT DEMONSTRATED: ninguna herramienta `make_pr` disponible |
| `gh pr create --base master --head fix/contrato-extensiones-cobra ...` | 4 | NOT DEMONSTRATED: falta autenticación; error literal documentado arriba |

Los comandos finales de revisión y commit se ejecutan después de escribir esta
adenda; sus resultados quedan corroborados por el estado Git; el intento de PR quedó bloqueado como se documenta arriba.
