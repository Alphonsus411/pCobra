# Cierre de integridad y CI (2026-08-11)

## Identidad

- **Fecha real de la validación:** 2026-08-11 (UTC).
- **Rama:** `work`.
- **SHA inicial del diferencial:**
  `96d70b1ba00f07608b0fc2a780fca0e7d6b09257` (baseline solicitado por las
  auditorías precedentes).
- **SHA final validado:**
  `7b866ab9dfd8467a02500a560031db172b1bf37d` (punta antes de este commit
  exclusivamente documental).
- **Baseline:** `96d70b1ba00f07608b0fc2a780fca0e7d6b09257`.
- **Snapshot canónico preformateo:**
  `f92f5f5863ef51d9722cdaea7a1c42619135e9a8`, padre inmediato del
  reformateo masivo `92e3291d41294255d3427217252d52fc6cdd3a02`.
- **Commit canónico de restauración:**

  ```text
  c84741ff8c9db12d4ccf70113a8d0ce88168d279
  fix(core): restore canonical lexer and parser snapshots
  ```

### Versiones

| Herramienta | Versión comprobada |
|---|---|
| Python | `3.12.13` (`/root/.pyenv/shims/python`) |
| pytest | `9.0.3` en la ejecución diferencial; CI fija `8.4.2` en `requirements-dev.txt` |
| Black | CI fija `26.5.1`; el ejecutable disponible al cierre es `26.3.1 (compiled: yes)` |
| Pylint | no instalado, no fijado y sin gate en los workflows (`python -m pylint`: `No module named pylint`) |
| CodeQL | action v3 fijada a `ad2a4837011b42f6947b78d6417e7c253b1c504b`; CLI local no instalada, por lo que su versión de bundle queda **pendiente** del runner remoto |

No se presenta la ausencia de Pylint o del CLI de CodeQL como un resultado
verde.

## Integridad Lexer/Parser

### Historia relevante y SHA canónico

El snapshot `f92f5f58` contenía los bytes canónicos. El commit masivo
`92e3291d` cambió formato y bytes de Lexer y Parser sin cambiar su AST de
Python. El commit independiente `c84741ff` restauró ambos archivos desde el
snapshot canónico; los merges posteriores conservaron esos bytes hasta
`7b866ab9`.

### Hashes antes y después

| Archivo | Después de `92e3291d` | Snapshot `f92f5f58` y current `7b866ab9` |
|---|---|---|
| `src/pcobra/cobra/core/lexer.py` | `7cf70380ab09b71961c138c0dfa6cf8721b69b78448f9c8109e7c1aac0db691f` | `537554f0cab9fb4ca456b2b99a43fca7b275241dcddfa5bb0fc3dcad78534e70` |
| `src/pcobra/cobra/core/parser.py` | `a0eaa2fc6a8139308cfd9012c713d91d2553a3af9b92ad1611a5c227eb8a9367` | `3017fa31e1707ca82358d548e71ba27d4b8e73342950ab6959b32c13dcc02505` |

El método estructural fue analizar con `ast.parse` el texto de cada revisión y
comparar `ast.dump(..., include_attributes=False)`: el reformateo conservaba
la estructura. Esa equivalencia semántico-estructural no se usó como sustituto
de la integridad byte a byte.

La restauración byte a byte se comprobó extrayendo cada blob mediante
`git show <sha>:<ruta> | sha256sum`: los hashes de `c84741ff`, el baseline,
`f92f5f58` y `7b866ab9` son idénticos. El guard
`python scripts/ci/gate_no_parser_lexer_changes.py --base 7b866ab9 --head HEAD`
termina en OK para este cierre documental.

## Syntax report

- **Comando exacto de CI:**
  `python scripts/ci/validate_syntax_report_contract.py`.
- **Traceback original reproducido:** `FileNotFoundError: [Errno 2] No such
  file or directory:
  'tests/data/snapshots/validar_sintaxis_report_schema_v1.json'`, originado en
  `main()` (línea 58) al ejecutar `SNAPSHOT_PATH.read_text(...)`; la cadena de
  llamadas fue módulo (línea 85) → `main` (línea 58) →
  `pathlib.Path.read_text` → `Path.open` → `io.open`.
- **Archivo responsable del contrato:**
  `scripts/ci/validate_syntax_report_contract.py`; consume el snapshot
  `tests/data/snapshots/validar_sintaxis_report_schema_v1.json`.
- **Clasificación:** referencia a fixture/snapshot ausente en un gate de
  contrato JSON, no fallo de sintaxis Cobra y no autorización para modificar
  Lexer o Parser.
- **Corrección mínima:** incorporar en un cambio independiente el snapshot JSON
  v1 que el propio gate referencia y verificar que su forma corresponde al
  payload; no se debe relajar la comparación ni capturar la excepción. Esa
  corrección no se mezcla con este commit documental.
- **Resultado posterior local:** **pendiente/fallido** (código 1 con el mismo
  `FileNotFoundError`); no se declara verde.

## CodeQL

El diagnóstico histórico afectó a
`.github/codeql/custom/unsafe-eval-exec.ql`, originalmente en línea 8,
columna 5 (`c.getTarget()`), seguido por usos no soportados de `getFile()` y
`regexp()`. El error original fue de resolución de miembros de la biblioteca
Python de CodeQL (el miembro `Call.getTarget()` no podía resolverse). La
versión exacta del bundle que emitió el diagnóstico no quedó persistida; solo
consta CodeQL Action v3 en el SHA indicado arriba, por lo que la versión del
CLI se marca **pendiente**.

`fe9a633c` sustituyó el constructo de resolución de target
`c.getTarget().hasQualifiedName(...)` por el equivalente soportado
`c.getFunc().(Name).getVariable()` enlazado a `GlobalVariable`, con
`getId() in ["eval", "exec"]`. También sustituyó `c.getFile()` por
`c.getLocation().getFile()` y `regexp()` por `regexpMatch()`.

Se preserva el significado porque la query sigue seleccionando llamadas a los
builtins globales `eval` y `exec`, sigue limitándose a `src/` y conserva la
única exclusión exacta `src/core/sandbox.py`. Los fixtures positivo y negativo
y `tests/test_codeql_config.py` fijan esas tres propiedades. El contrato local
pasa; el análisis CodeQL real queda **pendiente** porque el CLI no está
instalado y no se declara verde.

## Suite diferencial

Los contadores proceden de ejecuciones completas de `python -m pytest -q` con
el mismo entorno. `collected` es la suma de estados terminales.

| Estado | Baseline `96d70b1b` | Current `c228e70d` |
|---|---:|---:|
| collected | 4936 | 4941 |
| passed | 4372 | 4377 |
| failed | 507 | 507 |
| skipped | 54 | 54 |
| xfailed | 0 | 0 |
| errors | 3 | 3 |

### Diferencias normalizadas

1. **Fallos compartidos:** 493 pares `FAILED/ERROR + nodeid` únicos.
2. **Solo baseline:**
   `tests/unit/test_public_docs_scope.py::test_snippets_generados_siguen_sincronizados_con_la_fuente_canonica`.
3. **Solo current:**
   `tests/unit/test_security_sandbox.py::test_js_detecta_reemplazo_binario`.
4. **Nuevas regresiones atribuibles:** cero. El caso solo-current es una
   intermitencia histórica reproducida con el mismo mensaje (`DID NOT RAISE
   SecurityError`) y sin cambios funcionales atribuibles en test o sandbox.

La suite completa no está verde: conserva 507 fallos y 3 errores.

## CI

| Área | Estado | Evidencia |
|---|---|---|
| Tests | no verde | Diferencial completo anterior: 507 failed y 3 errors en current. |
| Syntax report | fallido | Código 1: falta `tests/data/snapshots/validar_sintaxis_report_schema_v1.json`. |
| Remote pytest | no ejecutado | No se lanzó un workflow remoto desde este cierre. |
| Lint/Black | verde en la validación previa | `black --check .` con la versión CI dejó 1157 archivos sin cambios; falta nueva ejecución con `26.5.1` en este entorno. |
| Pylint | no ejecutado | No existe gate, configuración ni dependencia instalada. |
| CodeQL | pendiente | Contratos textuales locales disponibles; análisis real requiere el runner/CLI. |

## Wheel e instalación aislada

El contrato `tests/cli/test_packaging_smoke.py` construye wheel y sdist,
inspecciona el wheel y exige que el único namespace importable top-level sea
`pcobra`. Después crea un `venv`, instala forzosamente el wheel y ejecuta desde
un directorio aislado que no contiene ni consulta el checkout. En ese proceso
comprueba tanto `find_spec` como la importación directa y confirma que no se
instalan ni resuelven paquetes top-level `core` o `cobra`. La ejecución dirigida
de este cierre resultó omitida porque el módulo opcional `build` no está
instalado; es una limitación de entorno y no evidencia verde de packaging.

## Inventario exacto y exclusiones protegidas

El único archivo modificado por este commit documental es:

```text
docs/auditorias/3465_cierre_integridad_ci_2026-08-11/README.md
```

Respecto de `7b866ab9`, no cambiaron archivos de grammar, definiciones de
tokens, ningún Lexer o Parser, `src/pcobra/core/optimizations/constant_folder.py`
ni `src/pcobra/core/ast_nodes.py`. Esta confirmación se limita al commit de
cierre y no reescribe la historia del diferencial auditado.

## Actualización de cierre de rama (2026-08-11 UTC)

### Identidad e inventario del diferencial de cierre

Para el cierre solicitado se toma como **SHA inicial causal**
`fdff35754e6903a171ea1990eeca951bf004e161`, padre de la serie que comienza
con la restauración canónica. La punta funcional antes de esta actualización
documental es `585d7bc9b2f2499c906d12fa844986543517e968`; el baseline histórico de las
ejecuciones completas continúa siendo
`96d70b1ba00f07608b0fc2a780fca0e7d6b09257`.

El diferencial `fdff3575..585d7bc9` contiene:

| Archivo | Clasificación y causa |
|---|---|
| `src/pcobra/cobra/core/lexer.py` | Restauración byte a byte desde el snapshot canónico `f92f5f58`; no introduce sintaxis. |
| `src/pcobra/cobra/core/parser.py` | Restauración byte a byte desde el mismo snapshot canónico; no introduce gramática. |
| `tests/data/snapshots/validar_sintaxis_report_schema_v1.json` | Snapshot v1 mínimo que ya exigía el gate de syntax report. |
| `.github/codeql/custom/unsafe-eval-exec.ql` | Compatibilidad de la query con la API AST Python disponible, sin ampliar el alcance semántico. |
| `tests/test_codeql_config.py` | Contratos focales de selección, alcance `src/` y exclusión exacta del sandbox. |
| `tests/unit/codeql_fixtures/unsafe_eval_exec/src/violation.py` | Fixture positivo focal de CodeQL. |
| `tests/unit/codeql_fixtures/unsafe_eval_exec/src/core/sandbox.py` | Fixture negativo para la única exclusión permitida. |
| `pyproject.toml` | Exclusión mínima de fixtures no-Python del barrido Black; pertenece al commit causal de lint `ec93f793`, no a runtime ni sintaxis. |
| `docs/auditorias/3450_runtime_security/README.md` | Evidencia histórica focal de seguridad runtime. |
| `docs/auditorias/3462_lint_diferencial/README.md` | Evidencia del diferencial Black/Pylint y su limitación de entorno. |
| `docs/auditorias/3464_pytest_tres_arboles/README.md` | Comparación por nodeid entre current, baseline y snapshot canónico. |
| `docs/auditorias/3465_cierre_integridad_ci_2026-08-11/README.md` | Informe nuevo y actualización de cierre. |

La presencia de `pyproject.toml` y de los tres informes antecedentes hace que
el diferencial acumulado sea algo más amplio que la lista ideal enunciada,
aunque son cambios de lint/evidencia causales ya separados y no afectan al
lenguaje. No se reescribe la historia para ocultarlos.

### Verificaciones locales finales

- `git diff --check`: código 0.
- `python -m compileall src`: código 0.
- `python scripts/ci/validate_syntax_report_contract.py`: código 0,
  `Contrato JSON de validar-sintaxis OK`.
- `python -m pytest -q tests/test_codeql_config.py`: 4 passed.
- `python -m pytest -q tests/test_lexer_parser_contract.py tests/test_lexer.py tests/test_parser.py`:
  13 passed.
- La suite focal combinada de syntax report obtuvo 4 passed y 1 fallo
  preexistente en
  `tests/unit/test_syntax_fixture_guard.py::test_existing_syntax_fixtures_were_not_modified`:
  `AssertionError: assert 18 == 9`; no se reduce esa aserción.
- `python -m pytest -q tests/cli/test_packaging_smoke.py`: 1 skipped y código
  5 porque `build` no está instalado; el wheel sigue sin resultado verde.
- El diferencial desde `fdff3575` no contiene cambios en rutas de grammar,
  tokens, `constant_folder.py` ni `src/pcobra/core/ast_nodes.py`.
- Los `.log` versionados bajo `docs/auditorias/3430_3431_repl/` son
  preexistentes y no aparecen en este diferencial. No se añadieron caches,
  `dist`, entornos virtuales, worktrees, dumps ni nuevos logs.

### Historia causal

Los cambios permanecen separados en `c84741ff` (core), `fe9a633c` (CodeQL),
`585d7bc9` (syntax report) y commits `docs(audit)` independientes. El cambio
de lint está aislado en `ec93f793`. Lexer y Parser proceden de
`f92f5f5863ef51d9722cdaea7a1c42619135e9a8`.

### Estado remoto

No se inventan resultados remotos: este checkout no tiene ningún remote
configurado y `gh auth status` informa que no hay autenticación para GitHub.
Por ello el push, la creación/actualización real de la PR, la inspección de
logs de Tests (incluido comprobar que alcanzó pytest), Lint, CodeQL y demás
required checks, así como la confirmación `OPEN`/sin auto-merge/base distinta
de `master`, quedan bloqueados por infraestructura. No se ejecutó merge,
squash, rebase, cierre ni operación sobre ramas protegidas.

## Continuación: evidencia final local y remota (2026-08-11 UTC)

Esta sección continúa el informe sin sustituir las validaciones anteriores.
Se separan los resultados obtenidos en el checkout de los publicados por
GitHub Actions y no se equipara inspección local con un gate remoto.

### Validación local

- El guard focal de integridad de Lexer y Parser terminó con `1 passed`:
  `python -m pytest -q tests/integration/test_usar_runtime_contract.py::test_integridad_estatica_lexer_y_parser_sin_diff_inesperado`.
- Git confirma mediante `merge-base --is-ancestor` que el snapshot
  `f92f5f5863ef51d9722cdaea7a1c42619135e9a8` y la restauración
  `c84741ff8c9db12d4ccf70113a8d0ce88168d279` pertenecen a esta rama.
- `python scripts/validate_runtime_contract.py` permanece **fallido**:
  `RuntimeError: Contrato usar canónico desalineado`; la matriz actual contiene
  módulos posteriores a los diez que fija la expectativa del script.
- `black --check .` permanece **fallido**: reformatearía
  `tests/test_codeql_config.py` y dejaría 1158 archivos sin cambios.
- Los conteos diferenciales completos conservados en este informe son:
  baseline 4936 collected, 4372 passed, 507 failed, 54 skipped y 3 errors;
  current 4941 collected, 4377 passed, 507 failed, 54 skipped y 3 errors.
  La diferencia es +5 collected y +5 passed, con 0 de diferencia en failed,
  skipped y errors; esto no convierte la suite completa en verde.

### Validación GitHub Actions

La evidencia remota final disponible corresponde exactamente al merge
`b727004c24bf8b68f4462a398bc6ea307ab5fcf8`. Todos los estados siguientes
son conclusiones publicadas por GitHub, no inferencias locales.

| Área solicitada | Run/job concreto | SHA probado | Conclusión literal |
|---|---|---|---|
| Tests | [run 31513615493, job 93853209936](https://github.com/Alphonsus411/pCobra/actions/runs/31513615493/job/93853209936) | `b727004c24bf8b68f4462a398bc6ea307ab5fcf8` | **failure**; `tier1-required (ubuntu-latest)` falló en `Validate runtime contract matrix`. |
| Lint | [run 31513615437, job 93853209610](https://github.com/Alphonsus411/pCobra/actions/runs/31513615437/job/93853209610) | `b727004c24bf8b68f4462a398bc6ea307ab5fcf8` | **failure** en `black --check .`; los pasos posteriores fueron `skipped`. |
| Black | [run 31513615437, job 93853209610](https://github.com/Alphonsus411/pCobra/actions/runs/31513615437/job/93853209610) | `b727004c24bf8b68f4462a398bc6ea307ab5fcf8` | **failure**. |
| CodeQL | [run 31513615454, job 93853209792](https://github.com/Alphonsus411/pCobra/actions/runs/31513615454/job/93853209792) | `b727004c24bf8b68f4462a398bc6ea307ab5fcf8` | **failure**. |
| Compatibility Regression Gate | [run 31513615493, job 93853210065](https://github.com/Alphonsus411/pCobra/actions/runs/31513615493/job/93853210065) | `b727004c24bf8b68f4462a398bc6ea307ab5fcf8` | No existe un check remoto con ese nombre exacto. El job real `Contractual compatibility gate` concluyó **success**; solo se atribuye el verde a ese job existente. |
| pytest remoto | [run 31513615493, job 93853209936](https://github.com/Alphonsus411/pCobra/actions/runs/31513615493/job/93853209936) | `b727004c24bf8b68f4462a398bc6ea307ab5fcf8` | **no ejecutado / skipped**: `Run tests` no se alcanzó tras el fallo previo. No hay conteo pytest remoto para este SHA. |

#### Lint: diagnóstico, corrección y resultado

El run original [31500087322](https://github.com/Alphonsus411/pCobra/actions/runs/31500087322),
sobre `30789f584d348b3891c0df8edd12e57b475bda54`, ejecutaba únicamente
`pip install "$(grep -E '^black==' requirements-dev.txt)"` antes de lanzar
`python scripts/validate_runtime_contract.py`. El traceback reproducido en ese
mismo árbol termina en:

```text
scripts/validate_runtime_contract.py
  -> pcobra.cobra.cli.target_policies
  -> pcobra.cobra.transpilers.runtime_api_matrix
  -> pcobra.standard_library.archivo
  -> pcobra.corelibs.red
ModuleNotFoundError: No module named 'requests'
```

La causa raíz fue que el workflow instalaba Black, pero no las dependencias de
runtime que el propio gate importaba. El commit
`6fc9b1dee310c562d1bc6b6b0de832ba2956d2fd` cambió ese paso por la action
compartida `./.github/actions/install`. El resultado remoto final no es verde:
el run 31513615437 se detuvo antes, en Black, y dejó el gate de runtime en
`skipped`. Localmente el import de `requests` ya no falla, pero el comando
alcanza y revela el `RuntimeError` contractual indicado arriba.

#### CodeQL: las tres evidencias del run

En el run [31513615454](https://github.com/Alphonsus411/pCobra/actions/runs/31513615454)
para el mismo SHA quedan registradas por separado las tres fases relevantes:

1. `Initialize CodeQL`: **success**.
2. `Test custom CodeQL queries`: **failure**.
3. `Perform CodeQL Analysis`: **skipped**.

Por ello CodeQL conserva conclusión global **failure**. Una inicialización
correcta no demuestra que las queries ni el análisis hayan pasado.
