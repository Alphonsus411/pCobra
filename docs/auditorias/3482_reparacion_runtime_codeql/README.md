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
