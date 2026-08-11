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
