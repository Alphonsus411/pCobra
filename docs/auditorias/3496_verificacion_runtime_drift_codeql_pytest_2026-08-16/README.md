# Auditoría 3496: Runtime, drift documental, CodeQL y full pytest (2026-08-16 UTC)

## Identidad, alcance y criterio de cierre

| Dato | Valor observado |
|---|---|
| `BASE_SHA` | `f82893a03d9c0446ce26f07636a8794ec0e2c581` |
| `FINAL_SHA` funcional auditado | `a55548f8051a92a2b6c86f7feb5ed8598dcc7fd1` |
| Rama | `work` |
| `master` antes / después | `NOT DEMONSTRATED`: la referencia local no existe en ninguno de los dos momentos |
| `origin/master` antes / después | `NOT DEMONSTRATED`: no hay remoto configurado ni referencia remota |

`FINAL_SHA` es el commit real del árbol funcional terminado y auditado. Este
documento se incorpora necesariamente en un commit documental posterior: un
commit no puede incluir su propio SHA sin cambiar recursivamente ese SHA.

**No se declara cierre global.** Aunque Runtime y documentation drift están en
`PASS`, CodeQL remoto está en `FAIL` y full pytest en `FAIL`/ejecución completa
`NOT DEMONSTRATED`. CodeQL local tampoco queda demostrado en este entorno.

## Archivos modificados

Lista completa de `BASE_SHA..FINAL_SHA`, seguida del propio documento de esta
auditoría (no se editó ninguna auditoría previa durante esta ronda):

```text
docs/LIBRO_PROGRAMACION_COBRA.md
docs/auditorias/3495_codeql_modalidad_2026-08-16/README.md
docs/standard_library/archivo.md
docs/standard_library/asincrono.md
docs/standard_library/datos.md
docs/standard_library/holobit.md
docs/standard_library/logica.md
docs/standard_library/numero.md
docs/standard_library/red.md
docs/standard_library/sistema.md
docs/standard_library/texto.md
docs/standard_library/tiempo.md
docs/auditorias/3496_verificacion_runtime_drift_codeql_pytest_2026-08-16/README.md
```

La auditoría 3495 ya formaba parte de `FINAL_SHA` al comenzar esta ronda; se
enumera por completitud del rango, no porque se haya modificado ahora.

## Runtime — PASS

Las 9 pruebas dirigidas pasaron y el validador declaró literalmente
`Runtime contract validation: OK`. No se modificaron Runtime, Lexer ni Parser.

## Documentation drift — PASS

`python scripts/sync_libro_programacion.py --check` terminó con exit 0 y
`Sin drift documental.` en `FINAL_SHA`. La causa del drift corregido entre la
base y el árbol final fueron **outputs autogenerados desincronizados respecto
de las fuentes consumidas por `scripts/sync_libro_programacion.py`**: el libro
y las fichas de `docs/standard_library/` son salidas generadas a partir de la
gramática, SPEC, comandos CLI y fuentes de `src/pcobra/standard_library` que el
script consume. No se cambiaron ejemplos para ocultar fallos.

## CodeQL local — NOT DEMONSTRATED

Las 9 pruebas de contrato de configuración pasaron, pero `command -v codeql`
terminó con exit 1 y tampoco existía el bundle esperado bajo `/tmp`. Por ello
no se presenta una compilación o análisis CodeQL local como `PASS`.

## Custom query harness — PASS remoto / NOT DEMONSTRATED local

El run remoto `31937073122`, job `95140570103`, completó `Test custom CodeQL
queries` con `success`. Localmente el harness no pudo ejecutarse por ausencia
del binario CodeQL. Las queries, fixtures, configuración y workflow no se
modificaron.

## CodeQL remoto — FAIL

El run público `31937073122` para `BASE_SHA` terminó en `failure`: Initialize,
Autobuild y custom query harness pasaron, pero `Perform CodeQL Analysis` falló.
La anotación pública informa que los análisis de configuraciones avanzadas no
pueden procesarse mientras Default setup esté habilitado. La causa del bloqueo
es, por tanto, la **coexistencia remota de Default setup con el workflow
Advanced setup versionado en `.github/workflows/codeql.yml`**. La API
administrativa respondió `401 Requires authentication`; no se falsea la
desactivación como realizada ni se extrapola el run de la base al SHA final.

Acción manual exacta requerida: `Settings` → `Security` → `Code security` →
`Code scanning` → `CodeQL`; desactivar `Default setup` y conservar `Advanced
setup`. Después debe relanzarse CodeQL y comprobarse un `PASS` nuevo.

## Full pytest — FAIL / finalización NOT DEMONSTRATED

El comando exacto de CI con cobertura no arrancó porque `pytest-cov` no está
instalado (exit 4). Un primer fallback incluyó `src/tests`, que no existe (exit
4). `pytest tests` recolectó 4.947 casos, avanzó al 39 % y ya acumulaba fallos;
se interrumpió tras 368,21 s con exit 2: `110 failed, 1810 passed, 25 skipped`.
Por ello hay evidencia suficiente para `FAIL`, pero no se afirma que la suite
completa llegase al final.

## Llegada del workflow `tests` a `Run tests` — NOT DEMONSTRATED

La consulta de runs remotos para `BASE_SHA` devolvió seis runs y ninguno se
llamaba `tests`; por tanto no existe evidencia de que ese workflow llegara al
paso `Run tests`. No hay remoto local ni credenciales para publicar o consultar
un run de `FINAL_SHA`.

## Hashes protegidos y referencias antes/después

| Archivo protegido | Antes | Después |
|---|---|---|
| `src/pcobra/cobra/core/lexer.py` | `50dbd208b1ff09c80462bca4036a8dcc84649be8` | `50dbd208b1ff09c80462bca4036a8dcc84649be8` |
| `src/pcobra/cobra/core/parser.py` | `cdcb0230e5ea4ea47ae710cbaccb38afde5b87d0` | `cdcb0230e5ea4ea47ae710cbaccb38afde5b87d0` |
| `src/pcobra/core/lexer.py` | `413cd9cdbf3835657cc766e645b1472bee11886c` | `413cd9cdbf3835657cc766e645b1472bee11886c` |
| `src/pcobra/core/parser.py` | `aad60be7f3f3e029c452937edf3c2e4656c59459` | `aad60be7f3f3e029c452937edf3c2e4656c59459` |
| `.github/workflows/codeql.yml` | `3378470872539b4921f9359303f14087799d6173` | `3378470872539b4921f9359303f14087799d6173` |
| `.github/codeql/custom/codeql-config.yml` | `117d54dc0b42b8d87793abdb1bf7b655fed60cb7` | `117d54dc0b42b8d87793abdb1bf7b655fed60cb7` |

`git rev-parse master` y `git rev-parse origin/master` devolvieron exit 128
antes; la repetición final produjo el mismo resultado. La referencia de rama
`work` pasó de `a55548f...` al commit exclusivamente documental de esta
auditoría; no se hizo checkout, merge ni mutación de `master`.

## Registro de comandos

`PASS` indica exit 0 y evidencia suficiente; `FAIL`, fallo observado del gate;
`NOT DEMONSTRATED`, ausencia de herramienta, credencial, referencia o una
ejecución que no terminó.

| Comando ejecutado | Exit | Clasificación y salida relevante |
|---|---:|---|
| `pwd` | 0 | PASS: `/workspace/pCobra` |
| `find .. -name AGENTS.md -print` | 0 | PASS: `../pCobra/AGENTS.md` |
| `find docs -type f` | 0 | PASS: localizó `docs/auditorias/<asunto>/README.md` |
| `git status --short --branch`; `git remote -v` | 0 | PASS para estado; remoto vacío, NOT DEMONSTRATED para CI final |
| `cat AGENTS.md` e inspecciones `cat`, `rg`, `sed`, `tail` y `find` de auditorías, scripts y workflows | 0 | PASS |
| `git rev-parse HEAD`; `git branch --show-current` | 0 | PASS: `a55548f...`, `work` |
| `git rev-parse master`; `git rev-parse origin/master` | 128 cada uno | NOT DEMONSTRATED: referencias inexistentes |
| `git hash-object` sobre los seis archivos protegidos | 0 | PASS: hashes de la tabla |
| `git cat-file -t BASE_SHA`; `git merge-base --is-ancestor BASE_SHA HEAD` | 0 | PASS: `commit`, ancestro confirmado |
| `python -m pytest -q tests/cli/test_runtime_imports_contract.py tests/unit/test_runtime_api_matrix_contract.py` | 0 | PASS: 9 passed |
| `python scripts/validate_runtime_contract.py` | 0 | PASS: `Runtime contract validation: OK` |
| `python scripts/sync_libro_programacion.py --check` | 0 | PASS: `Sin drift documental.` |
| `python -m pytest -q tests/test_codeql_config.py` | 0 | PASS: 9 passed |
| `command -v codeql`; `test -x /tmp/codeql-bundle-2.26.3/codeql/codeql` | 1 cada uno | NOT DEMONSTRATED: binario ausente |
| `gh auth status` | 1 | NOT DEMONSTRATED: sin sesión |
| `curl https://api.github.com/repos/Alphonsus411/pCobra/code-scanning/default-setup` | 0, HTTP 401 | NOT DEMONSTRATED: `Requires authentication` |
| `curl .../actions/runs?head_sha=BASE_SHA&per_page=100` y lector Python JSON | 0, HTTP 200 | PASS: 6 runs inventariados; ninguno `tests` |
| `curl .../actions/runs/31937073122/jobs` y lector Python JSON | 0, HTTP 200 | FAIL remoto: Analysis falló; harness pasó |
| `curl .../commits/BASE_SHA/check-runs` y lector Python JSON | 0, HTTP 200 | PASS de consulta; check `analyze` en failure |
| `curl .../check-runs/95140570103/annotations` y lector Python JSON | 0, HTTP 200 | FAIL remoto: coexistencia Default/Advanced literal |
| `pytest tests src/tests --cov=src --cov-report=xml --cov-fail-under=95` | 4 | FAIL: argumentos `--cov` no reconocidos |
| `pytest tests src/tests` | 4 | FAIL: `src/tests` inexistente |
| `pytest tests` | 2 | FAIL / NOT DEMONSTRATED: 110 fallos antes de interrupción al 39 % |
| `git diff --name-only BASE_SHA..FINAL_SHA`; `git diff --stat BASE_SHA..FINAL_SHA`; `git status --short` | 0 | PASS: inventario y estado revisados |

Los polls de los procesos pytest (`write_stdin`/esperas del ejecutor) no son
comandos de repositorio; sus salidas incrementales forman parte del resultado
del comando pytest correspondiente. Los chequeos finales, commit y creación de
PR ocurren después de redactar el documento y se informan en la entrega.
