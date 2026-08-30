# Auditoría 3482: reparación Runtime API y CodeQL

## Estado, base y HEAD

- **Estado global: PENDIENTE.** La restauración de los cuatro aliases y la
  reparación de `ast-no-type-validation.ql` están demostradas, pero el contrato
  Runtime continúa bloqueado por el hallazgo independiente
  `obtener_url_texto`, que esta ronda prohíbe corregir.
- `BASE_SHA`: `f3bec17bab295c760fcdedf4d74703e21d512e39`.
- `HEAD` funcional auditado inicialmente: `888661ff646cdd9883e4e1583e27ed1af91bf038`; la revalidación final y su SHA se documentan al final.
- Rama: `fix/contrato-extensiones-cobra`.
- El commit documental posterior que contiene este informe no puede
  autorreferenciar su propio SHA; se comunica junto con el PR.

## Archivos modificados

1. `.github/codeql/custom/ast-no-type-validation.ql`
2. `.github/codeql/custom/codeql-config.yml`
3. `.github/codeql/custom/test/ast_no_type_validation/insecure/ast-no-type-validation.expected`
4. `.github/workflows/codeql.yml`
5. `src/pcobra/cobra/transpilers/runtime_api_parity_snapshot.json`
6. `src/pcobra/corelibs/__init__.py`
7. `tests/test_codeql_config.py`
8. `tests/unit/test_runtime_api_matrix_contract.py`
9. `docs/auditorias/3482_reparacion_runtime_codeql/README.md`

El archivo `.expected` no se editó manualmente: se actualizó mediante
`codeql test accept` después de comprobar que la query producía exactamente
las dos alertas inseguras previstas con CodeQL 2.26.3. No se escribieron
artefactos Runtime generados porque el generador falló antes de esa fase.

## Restauración de la API pública

La regresión había retirado del agregador `pcobra.corelibs` cuatro aliases que
ya eran públicos. Se restauraron literalmente sus imports históricos y sus
entradas en `__all__`:

- `unir_ruta` (`ruta.unir`);
- `leer_json_serializacion` (`serializacion.leer_json`);
- `ejecutar_proceso` (`proceso.ejecutar`);
- `info_registro` (`registro.info`).

El snapshot canónico vuelve a incluir los cuatro en la API global Python y en
`python.corelibs`. La prueba contractual ya no exige su ausencia: exige su
presencia en ambos conjuntos. Se conservaron sin cambios de decisión
`contiene`, `falso`, `igual`, `lanza_error`, `leer_configuracion`, `leer_ini`,
`leer_toml`, `toml_disponible` y `verdadero`.

Los cuatro imports directos finalizaron en **PASS**:

```python
from pcobra.corelibs import unir_ruta
from pcobra.corelibs import leer_json_serializacion
from pcobra.corelibs import ejecutar_proceso
from pcobra.corelibs import info_registro
```

## Causa de `FunctionCall` y solución demostrada

La API AST de Python disponible en el bundle oficial CodeQL 2.26.3 no define
el tipo `FunctionCall`; representa una llamada con `Call`. La inspección de la
biblioteca oficial mostró `class Call extends Call_`, `Call.getFunc()` para el
callable y `Name.getId()` para el identificador. La ejecución real reveló
además que los métodos Python se representan con `Function` dentro del scope
`Class`, no con `Method`, y que el predicado soportado es `regexpMatch`.

La query ahora:

- selecciona clases cuyo nombre cumple `^Nodo.*`;
- busca `Function m` con `m.getScope() = c` y nombre `__post_init__`;
- acepta una `Call` a un `Name` llamado `isinstance` dentro de ese método, o un
  `Assert` cuyo scope sea ese método;
- reporta la clase cuando no existe ninguna de esas validaciones.

Se añadieron metadatos QLDoc válidos para evitar que una advertencia de
compilación contaminara los resultados del test. La finalidad no se debilitó:
el fixture seguro no genera alertas y el inseguro genera las dos esperadas.

CI ejecuta ahora ambos directorios de pruebas custom con el `codeql-path`
producido por el paso `Initialize CodeQL`. La configuración productiva ignora
además `.github/codeql/custom/test/ast_no_type_validation/**`, de modo que los
fixtures intencionadamente inseguros continúan ejecutables con `codeql test
run` sin convertirse en alertas productivas.

## Resultados exactos

| Verificación | Estado | Resultado exacto |
|---|---|---|
| Pruebas focales Runtime API/corelibs/usar | **PENDIENTE** | `1 failed, 59 passed, 1 skipped in 2.58s`; único fallo: bloqueo independiente `obtener_url_texto`. |
| Generador Runtime | **PENDIENTE / bloqueo independiente** | Código 1; `RuntimeError: Snapshot inválido para python.corelibs: símbolos desconocidos ['obtener_url_texto']`. No se corrigió y no escribió artefactos. |
| Validador Runtime | **FAIL derivado/preexistente** | Código 1; `cobra.system.ejecutar_comando_async.python: marcado full pero no aparece en runtime_api_matrix.available_api_by_backend.global`. La matriz permanece antigua porque el generador se detuvo. |
| Imports de los cuatro aliases | **PASS** | Código 0; los cuatro objetos importaron correctamente. |
| Configuración/triggers CodeQL | **PASS** | `8 passed in 0.21s`; código 0. |
| `ast_no_export_validation` real | **PASS** | `All 2 tests passed`; código 0. |
| `ast_no_type_validation` real final | **PASS** | `All 2 tests passed`; código 0. |
| Black focal | **PASS** | `3 files would be left unchanged`; código 0. |
| `git diff --check` | **PASS** | Sin salida; código 0. |
| Integridad Lexer/Parser | **PASS** | Los cuatro SHA-256 finales coinciden con los iniciales. |

### Comandos realmente ejecutados

```console
$ python -m pytest -q tests/unit/test_runtime_api_matrix_contract.py tests/unit/test_corelibs_configuracion.py tests/unit/test_corelibs_pruebas.py tests/unit/test_corelibs_sistema.py tests/unit/test_usar_core_all_exports.py tests/test_usar_public_exports_snapshot.py tests/cli/test_runtime_imports_contract.py tests/integration/test_usar_runtime_contract.py
1 failed, 59 passed, 1 skipped in 2.58s
[exit 1]

$ python scripts/generar_matriz_api_runtime.py
RuntimeError: Snapshot inválido para python.corelibs: símbolos desconocidos ['obtener_url_texto']
[exit 1]

$ python scripts/validate_runtime_contract.py
pcobra.cobra.stdlib_contract.validator.ContractValidationError: cobra.system.ejecutar_comando_async.python: marcado full pero no aparece en runtime_api_matrix.available_api_by_backend.global
[exit 1]

$ python -m pytest -q tests/test_codeql_config.py tests/unit/test_codeql_triggers.py
8 passed in 0.21s
[exit 0]

$ python -c 'from pcobra.corelibs import unir_ruta; from pcobra.corelibs import leer_json_serializacion; from pcobra.corelibs import ejecutar_proceso; from pcobra.corelibs import info_registro; print(unir_ruta, leer_json_serializacion, ejecutar_proceso, info_registro)'
<function unir ...> <function leer_json ...> <function ejecutar ...> <function info ...>
[exit 0]

$ /tmp/codeql-bundle-3482/codeql/codeql version
CodeQL command-line toolchain release 2.26.3.
[exit 0]

$ /tmp/codeql-bundle-3482/codeql/codeql test run .github/codeql/custom/test/ast_no_export_validation
All 2 tests passed.
[exit 0]

$ /tmp/codeql-bundle-3482/codeql/codeql test accept .github/codeql/custom/test/ast_no_type_validation/insecure/ast-no-type-validation.qlref
Accepted .../ast-no-type-validation.qlref.
[exit 0]

$ /tmp/codeql-bundle-3482/codeql/codeql test run .github/codeql/custom/test/ast_no_type_validation
All 2 tests passed.
[exit 0]

$ black --check src/pcobra/corelibs/__init__.py tests/test_codeql_config.py tests/unit/test_runtime_api_matrix_contract.py
All done! 3 files would be left unchanged.
[exit 0]

$ git diff --check
[sin salida]
[exit 0]
```

## Bloqueo Runtime literal y criterio de parada

El generador volvió a alcanzar exactamente el bloqueo independiente solicitado:

```text
RuntimeError: Snapshot inválido para python.corelibs: símbolos desconocidos ['obtener_url_texto']
```

**Se detuvo la corrección Runtime. No se corrigió `obtener_url_texto` en esta
ronda.** Tampoco se intentó regenerar o editar manualmente la matriz después de
ese fallo. El error posterior del validador se registra sin ampliar alcance.

## Integridad de Lexer/Parser y superficies prohibidas

Hashes iniciales y finales, idénticos byte a byte:

```text
537554f0cab9fb4ca456b2b99a43fca7b275241dcddfa5bb0fc3dcad78534e70  src/pcobra/cobra/core/lexer.py
3017fa31e1707ca82358d548e71ba27d4b8e73342950ab6959b32c13dcc02505  src/pcobra/cobra/core/parser.py
fbd130d88ec6255c1e966752730a7cb2e2311c50125d85df487fc67d55aaf61e  src/pcobra/core/lexer.py
656d9c911ab0760435efc48502625b6016955f00d0429228a0ffced87e982a2b  src/pcobra/core/parser.py
```

La revisión de nombres y del diff confirma que no se modificaron Lexer,
Parser, `interpreter.py`, implementaciones AST, gramática, `constant_folder`,
sandbox/security, `red.py`, `compresion.py`, `proceso.py`, `sistema.py`,
procesos seguros ni `validator_worker`. La aparición de `ast` en dos rutas del
diff corresponde exclusivamente a la query CodeQL autorizada y a su resultado
esperado, no al AST del Core. No se cambió comportamiento del Core ni sintaxis
Cobra y no se tocó `master`.

## Revalidación final de la rama (2026-08-15 UTC)

El SHA funcional final revisado antes del commit exclusivamente documental es
`d3b10012633b8ba3e409682671cd69d27759eb64`. Esta precisión evita afirmar que
un commit contiene su propio identificador: el SHA del commit del informe se
registra en el historial Git y en la PR.

La revalidación se ejecutó en el orden solicitado y se detuvo al aparecer el
fallo independiente del validador, de acuerdo con el criterio de parada. No se
hicieron correcciones Runtime ni se modificaron red, sandbox o semántica:

```console
$ python -m pytest -q tests/unit/test_runtime_api_matrix_contract.py tests/unit/test_corelibs_configuracion.py tests/unit/test_corelibs_pruebas.py tests/unit/test_corelibs_sistema.py tests/unit/test_usar_core_all_exports.py tests/test_usar_public_exports_snapshot.py tests/cli/test_runtime_imports_contract.py tests/integration/test_usar_runtime_contract.py
1 failed, 59 passed, 1 skipped in 2.50s
RuntimeError: Snapshot inválido para python.corelibs: símbolos desconocidos ['obtener_url_texto']
[exit 1; PENDIENTE]

$ python scripts/generar_matriz_api_runtime.py
RuntimeError: Snapshot inválido para python.corelibs: símbolos desconocidos ['obtener_url_texto']
[exit 1; PENDIENTE]

$ python scripts/validate_runtime_contract.py
pcobra.cobra.stdlib_contract.validator.ContractValidationError: cobra.system.ejecutar_comando_async.python: marcado full pero no aparece en runtime_api_matrix.available_api_by_backend.global
[exit 1; FAIL]
```

La evidencia literal del bloqueo exigido es:

```text
RuntimeError: Snapshot inválido para python.corelibs: símbolos desconocidos ['obtener_url_texto']
```

Por la parada obligatoria ante el segundo fallo independiente, en esta
revalidación quedaron **PENDIENTE** los tests de configuración CodeQL, ambos
`codeql test run`, la comprobación ejecutable de los cuatro imports y
`black --check`. Sus ejecuciones reales anteriores, incluidos el
`codeql-path` real `/tmp/codeql-bundle-3482/codeql/codeql`, permanecen
registradas arriba sin presentarlas falsamente como una nueva ejecución.

## Enmienda trazable posterior: tareas A y B (2026-08-16 UTC)

Esta sección es una adenda: conserva el relato anterior como evidencia
histórica y corrige expresamente sus datos sin reescribirlos.

### Corrección del SHA histórico y límites de la revalidación

El valor `d3b10012633b8ba3e409682671cd69d27759eb64` consignado arriba es un
**dato histórico erróneo**. El SHA correcto del merge de la PR #3484 es
`d3b10012fe393633891925e4807df3b70197c8bd`. La enmienda se debe a que el
valor anterior no identifica ningún commit del historial disponible, mientras
que `git show -s --format='%H %s' d3b10012fe393633891925e4807df3b70197c8bd`
resuelve el merge esperado. El dato erróneo no se borra para mantener visible
la cadena de auditoría.

Para las tareas A y B, el `BASE_SHA` real es
`6c75e34e69016427348a32870c71d386788e550d` y el `HEAD_SHA` funcional final
real es `6868e33562d438aafe3de42820d7cd51f08b3607`. La rama de trabajo documental
es `fix/contrato-extensiones-cobra`. Este `HEAD_SHA` designa el estado final
de las dos tareas antes del commit que incorpora la presente adenda; no se
pretende que un commit se autorreferencie.

- **Tarea A:** el commit `2af7edee8760f6d22368540b04e039a34ded6fa4`
  volvió a exponer `obtener_url_texto` desde el agregador público y añadió
  comprobaciones contractuales. Es una exportación pública ya existente: la
  función estaba implementada y el contrato `cobra.web.obtener_url_texto`
  ya declaraba soporte Python `full`; no se inventó un alias ni sintaxis.
- **Tarea B:** el commit `9b30ac702fd06aeb4b0eb6a6aeb1ecd74be09d7b`
  añadió a `missing-codegen-exception.ql` exclusivamente metadata QLDoc
  (`@kind problem`, severidad e identificador) y una prueba de presencia de
  `@kind`. El `from`, el `where` y el `select` de la query permanecieron
  idénticos: **no hubo cambio lógico**.

Los archivos modificados por A y B, y sólo éstos, fueron:

1. `src/pcobra/corelibs/__init__.py`;
2. `tests/cli/test_runtime_imports_contract.py`;
3. `tests/unit/test_runtime_api_matrix_contract.py`;
4. `.github/codeql/custom/missing-codegen-exception.ql`;
5. `tests/test_codeql_config.py`.

La presente ronda modifica exclusivamente
`docs/auditorias/3482_reparacion_runtime_codeql/README.md`. No existe una ref
local `master` ni una ref local de seguimiento `origin/master`; no se ejecutó
merge ni push y `master` **no fue tocado**. La consulta remota de sólo lectura
registró `8b1676cdf52f30147ce42584a98ca4c421756369` para `master` antes de crear el
commit documental.

### Evidencia remota sobre el SHA base

La API pública de GitHub aporta evidencia trazable para
`6c75e34e69016427348a32870c71d386788e550d` en los runs CodeQL
[`31898923095`](https://github.com/Alphonsus411/pCobra/actions/runs/31898923095)
y [`31901256502`](https://github.com/Alphonsus411/pCobra/actions/runs/31901256502):

- `Test custom CodeQL queries` (paso 6) terminó `completed/success`:
  **PASS**. Por tanto, `ast-no-type-validation` ya no era el blocker.
- `Perform CodeQL Analysis` (paso 7) terminó `completed/failure`: **FAIL
  preexistente en el SHA base**.
- Las anotaciones de los jobs
  [`95046414355`](https://github.com/Alphonsus411/pCobra/actions/runs/31898923095/job/95046414355)
  y [`95052284291`](https://github.com/Alphonsus411/pCobra/actions/runs/31901256502/job/95052284291)
  atribuyen el fallo a que `interpret-results` no pudo procesar
  `missing-codegen-exception.bqrs`: la query carecía de la propiedad metadata
  `@kind` (`NO_KIND_SPECIFIED`). Esta es la causa demostrada remotamente, no
  una inferencia a partir del resultado global del workflow.
- La primera comprobación Runtime registrada al partir de ese SHA estaba
  bloqueada por `RuntimeError: Snapshot inválido para python.corelibs:
  símbolos desconocidos ['obtener_url_texto']`. Es un bloqueo preexistente de
  A, distinto del fallo de metadata que resolvió B.

### Comandos, códigos de salida y atribución

| Comando exacto | Código | Estado y resultado |
|---|---:|---|
| `git show -s --format='%H %s' d3b10012fe393633891925e4807df3b70197c8bd` | 0 | **PASS**; resolvió `d3b10012fe393633891925e4807df3b70197c8bd Merge pull request #3484 ...`. |
| `python -m pytest -q tests/cli/test_runtime_imports_contract.py tests/unit/test_runtime_api_matrix_contract.py` | 1 | **FAIL preexistente/no atribuible a esta adenda**; `1 failed, 8 passed`: snapshot desactualizado, nuevo símbolo sin mapear `obtener_url_texto`. La prueba de import público sí pasó. |
| `python scripts/generar_matriz_api_runtime.py` | 1 | **FAIL preexistente/no atribuible a esta adenda**; `Snapshot de API Python desactualizado ... Nuevos símbolos sin mapear: ['obtener_url_texto']`. |
| `python scripts/validate_runtime_contract.py` | 1 | **FAIL preexistente/no atribuible a esta adenda**; `cobra.system.ejecutar_comando_async.python` está marcado `full` pero no aparece en la matriz global. |
| `python -m pytest -q tests/test_codeql_config.py` | 0 | **PASS**; `9 passed in 0.06s`, incluida la prueba de metadata de B. |
| `/tmp/codeql-bundle-3482/codeql/codeql test run .github/codeql/custom/test/ast_no_export_validation .github/codeql/custom/test/ast_no_type_validation` | no ejecutado | **warning / NOT DEMONSTRATED en esta revalidación**; el binario no estaba presente. Se mantiene separada la evidencia remota PASS del SHA base. |
| `git show-ref --verify refs/heads/master` | 128 | **warning**; la ref local no existe. Confirma que esta ronda no operó sobre una rama local `master`, pero por sí solo no prueba el estado remoto. |
| `git show-ref --verify refs/remotes/origin/master` | 128 | **warning**; no existe remote-tracking ref porque este checkout no tiene `origin`. |
| `python - <<'PY' ... urllib.request.urlopen('https://api.github.com/repos/Alphonsus411/pCobra/branches/master') ... PY` | 0 | **PASS**; consulta remota de sólo lectura: `master` = `8b1676cdf52f30147ce42584a98ca4c421756369`. |
| `git diff --check` | 0 | **PASS**; sin salida. |
| `git diff --name-only` | 0 | **PASS**; sólo `docs/auditorias/3482_reparacion_runtime_codeql/README.md`. |
| `for f in src/pcobra/cobra/core/lexer.py src/pcobra/cobra/core/parser.py src/pcobra/core/lexer.py src/pcobra/core/parser.py; do printf '%s  %s\n' "$(git hash-object "$f")" "$f"; done` | 0 | **PASS**; produjo exactamente los cuatro Git blob SHA exigidos. |
| `git diff --name-only -- src/pcobra/cobra/core/lexer.py src/pcobra/cobra/core/parser.py src/pcobra/core/lexer.py src/pcobra/core/parser.py` | 0 | **PASS**; sin salida, ninguna superficie protegida cambió. |

Los fallos Runtime son deuda funcional del estado recibido y no fueron
causados por esta modificación exclusivamente documental. La prueba focal
confirma el import introducido por A, pero A no deja verde el generador: el
símbolo pasó de «desconocido en los exports» a «nuevo sin mapear». B sí corrige
la causa remota `NO_KIND_SPECIFIED`; la suite de configuración local pasa,
pero el análisis CodeQL completo posterior queda **NOT DEMONSTRATED** en esta
revalidación.

### Integridad de superficies protegidas

Antes de editar esta adenda, `git hash-object` produjo estos Git blob SHA, que
coinciden exactamente con los valores exigidos:

```text
50dbd208b1ff09c80462bca4036a8dcc84649be8  src/pcobra/cobra/core/lexer.py
cdcb0230e5ea4ea47ae710cbaccb38afde5b87d0  src/pcobra/cobra/core/parser.py
413cd9cdbf3835657cc766e645b1472bee11886c  src/pcobra/core/lexer.py
aad60be7f3f3e029c452937edf3c2e4656c59459  src/pcobra/core/parser.py
```

Después de editar y revisar el diff, la misma comprobación produjo exactamente
los mismos cuatro valores. La comprobación dirigida con `git diff --name-only`
no produjo rutas: Lexer y Parser no se han modificado.

### Estado de cierre

**No se declara cierre global.** El generador y el validador Runtime no
finalizan correctamente, y el análisis CodeQL completo posterior a B no está
demostrado como PASS. El alcance queda documentado como avance incremental:
export público e import focal de A demostrados, metadata de B demostrada, y
deuda Runtime/análisis completo todavía abierta.
