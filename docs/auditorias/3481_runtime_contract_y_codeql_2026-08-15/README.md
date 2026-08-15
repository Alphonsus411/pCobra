# Auditoría 3481: Runtime Contract y `ast-no-type-validation`

## Estado, base y trazabilidad Git

**Estado final: `PENDIENTE`.** La reconciliación de los trece símbolos está
implementada y sus pruebas focales pasan, pero el Runtime Contract no puede
quedar verde por el bloqueo nuevo e independiente `obtener_url_texto`. Además,
`Perform CodeQL Analysis` terminó en **FAIL** en la evidencia remota
posterior; sus logs requieren autenticación (HTTP 403), por lo que la atribución
concreta queda **NOT DEMONSTRATED** y nunca se declara `PASS`.

- `BASE_SHA`: `44895816fc54ae0c2dea2ad19e48d4fcdc7fc793`.
- Rama de trabajo local: `work` (continuación del flujo de
  `fix/contrato-extensiones-cobra`; el PR debe dirigirse a esa rama, nunca a
  `master`).
- HEAD funcional auditado antes del commit documental:
  `a7a7f2f1` (`git rev-parse HEAD`). El SHA del commit que contiene este informe
  no puede autorreferenciarse dentro de su propio contenido; se debe resolver
  con `git rev-parse HEAD` tras el commit y queda comunicado junto al PR.
- Commits de cambio desde la base, sin contar merges:
  - `89d869b388b1caa3ff7c26baf8ac406e9702e9e4`: reconciliación runtime.
  - `716972be9ee26170e61f51f46601097dd1e6b6ac`: query y prueba CodeQL.
  - `a7a7f2f1`: normalización Black focal posterior, sin cambio semántico.
- Los merges intermedios son `1544b49196e8f99979875eed2579ffe2aa3dbc84`
  y `77d57da4ac23aea4bdfc8f72fa4c8786bbc8d193`.

## Criterio A/B/C/D/E y decisión individual de los trece símbolos

La clasificación se aplicó de forma individual y conservadora:

- **A**: implementación real y exportación pública agregada intencional; debe
  incorporarse al snapshot Python y, por generación, a la matriz.
- **B**: alias de conveniencia de un módulo especializado que no constituye API
  agregada canónica; se elimina solo del agregador, conservando la interfaz del
  módulo propietario.
- **C**: símbolo público que exigiría adaptación de implementación.
- **D**: símbolo obsoleto que exigiría retirada incompatible.
- **E**: no resoluble sin tocar Lexer, Parser o sintaxis; obliga a detenerse.

No hubo símbolos C, D o E.

| Símbolo | Clase | Evidencia concreta | Decisión |
|---|---:|---|---|
| `contiene` | A | Implementado en `corelibs/pruebas.py`; importado y listado en `corelibs.__all__`. | Añadir a `python_global_api_snapshot` y `python.corelibs`. |
| `falso` | A | Implementado en `corelibs/pruebas.py`; importado y listado en `corelibs.__all__`. | Añadir a ambas listas Python del snapshot. |
| `igual` | A | Implementado en `corelibs/pruebas.py`; importado y listado en `corelibs.__all__`. | Añadir a ambas listas Python del snapshot. |
| `lanza_error` | A | Implementado en `corelibs/pruebas.py`; importado y listado en `corelibs.__all__`. | Añadir a ambas listas Python del snapshot. |
| `leer_configuracion` | A | Implementado en `corelibs/configuracion.py`; importado y listado en `corelibs.__all__`. | Añadir a ambas listas Python del snapshot. |
| `leer_ini` | A | Implementado en `corelibs/configuracion.py`; importado y listado en `corelibs.__all__`. | Añadir a ambas listas Python del snapshot. |
| `leer_toml` | A | Implementado en `corelibs/configuracion.py`; importado y listado en `corelibs.__all__`. | Añadir a ambas listas Python del snapshot. |
| `toml_disponible` | A | Implementado en `corelibs/configuracion.py`; importado y listado en `corelibs.__all__`. | Añadir a ambas listas Python del snapshot. |
| `verdadero` | A | Implementado en `corelibs/pruebas.py`; importado y listado en `corelibs.__all__`. | Añadir a ambas listas Python del snapshot. |
| `ejecutar_proceso` | B | Era alias agregado de `corelibs.proceso.ejecutar`; el módulo `proceso` sigue siendo público. | Retirar import y entrada de `corelibs.__all__`; no inventar otro nombre. |
| `info_registro` | B | Era alias agregado de `corelibs.registro.info`; el módulo `registro` sigue siendo público. | Retirar solo el alias del agregador. |
| `leer_json_serializacion` | B | Era alias agregado de `corelibs.serializacion.leer_json`; el módulo sigue siendo público. | Retirar solo el alias del agregador. |
| `unir_ruta` | B | Era alias agregado de `corelibs.ruta.unir`; el módulo `ruta` sigue siendo público. | Retirar solo el alias del agregador. |

La prueba `test_python_runtime_preserves_documented_extension_exports_only`
fija ambas decisiones: exige los nueve A en la disponibilidad Python y prohíbe
que los cuatro B reaparezcan en la API global. No se cambió la documentación ni
se debilitó ninguna aserción para ocultar un fallo.

## Flujo contractual demostrado

1. La **implementación real** reside en los módulos `corelibs/configuracion.py`,
   `corelibs/pruebas.py` y, para el hallazgo anterior,
   `corelibs/sistema.py` (`ejecutar_comando_async`).
2. `src/pcobra/corelibs/__init__.py` importa los objetos públicos y los enumera
   en su `__all__`; los cuatro aliases B fueron retirados de ambos sitios.
3. `runtime_api_matrix.extract_runtime_export_sets()` lee literalmente los
   `__all__` de `standard_library` y `corelibs`; el snapshot canónico
   `runtime_api_parity_snapshot.json` declara qué parte está disponible por
   backend y detecta deriva antes de generar.
4. `scripts/generar_matriz_api_runtime.py` valida el snapshot, construye la
   matriz y solo entonces escribe `docs/_generated/runtime_api_matrix.json` y
   `.md`.
5. `scripts/validate_runtime_contract.py` consume la matriz derivada mediante
   los validadores de contratos y contrasta las políticas públicas.

`ejecutar_comando_async` recorrió exactamente esa cadena: existe en
`corelibs/sistema.py`, se importa y publica en `corelibs.__all__`, figura en las
listas Python canónicas del snapshot y la prueba focal confirma su presencia en
`available_api_by_backend.python.global`. En esta ejecución, sin embargo, el
generador se detuvo **antes de escribir** la matriz derivada por el bloqueo
independiente literal indicado abajo; por eso el JSON derivado conservado aún no
lo contiene y el validador posterior también falla. Esta ejecución no se
presenta falsamente como `PASS`.

## Resultados: PASS, fallos y no demostrado

| Resultado | Clasificación | Código / evidencia relevante |
|---|---|---|
| Generador | **bloqueo nuevo independiente** | Código 1: snapshot contiene `obtener_url_texto`, desconocido para los exports actuales. No escribió artefactos. |
| Runtime Contract | **FAIL preexistente derivado del bloqueo independiente** | Código 1: `ejecutar_comando_async` no está en la matriz derivada aún conservada. No es regresión de los trece símbolos. |
| Prueba focal matriz | **FAIL preexistente / bloqueo nuevo independiente** | 1 failed, 4 passed; solo falla la validación del snapshot por `obtener_url_texto`; pasan la reconciliación de los trece y `ejecutar_comando_async`. |
| Pruebas focales de `configuracion`, `pruebas`, `sistema` | **PASS** | 28 passed, 1 skipped; código 0. |
| Contratos de exports/API pública | **PASS** | 27 passed; código 0. |
| Pruebas Python de configuración/triggers CodeQL | **PASS** | 7 passed; código 0. Estas no sustituyen al CLI CodeQL. |
| Test focal real `ast-no-type-validation` con CLI local | **NOT DEMONSTRATED** | `command -v codeql` no encontró CLI; no se simuló su ejecución. |
| Suite completa de queries custom local | **NOT DEMONSTRATED** | CLI no disponible; no ejecutable localmente. |
| Evidencia remota histórica `Test custom CodeQL queries` | **PASS** | Runs `31883801009` y `31883799363`, job `analyze`, paso 6: `completed/success` sobre `716972be...`. |
| Evidencia remota posterior del merge `Test custom CodeQL queries` | **PASS** | Run `31883982010`, job `95010443113`, paso 6: `completed/success` sobre `77d57da4...`. |
| `Perform CodeQL Analysis` posterior | **FAIL; atribución NOT DEMONSTRATED** | Run `31883982010`, job `95010443113`, paso 7: `completed/failure`. La descarga anónima de logs devolvió HTTP 403; no se inventa una causa ni se atribuye a este cambio sin evidencia. |
| Black inicial | **FAIL atribuible** | Código 1: una línea en la prueba focal requería normalización. Se corrigió sin cambio semántico y se repitió. |
| Black final | **PASS** | Se registra en las verificaciones finales. |

No se ejecutó el conjunto completo porque el Runtime Contract no quedó verde;
esto sigue literalmente la condición de no ampliar alcance ni corregir fallos
históricos/independientes.

## Bloqueos nuevos literales

Generador, código 1:

```text
RuntimeError: Snapshot inválido para python.corelibs: símbolos desconocidos ['obtener_url_texto']
```

Runtime Contract, código 1:

```text
pcobra.cobra.stdlib_contract.validator.ContractValidationError: cobra.system.ejecutar_comando_async.python: marcado full pero no aparece en runtime_api_matrix.available_api_by_backend.global
```

CodeQL remoto posterior al merge, al cierre:

```text
Test custom CodeQL queries: completed / success
Perform CodeQL Analysis: completed / failure
Descarga anónima de logs: HTTP Error 403: Forbidden
```

## Integridad de Lexer/Parser y superficies sensibles

SHA-256 inicial:

```text
537554f0cab9fb4ca456b2b99a43fca7b275241dcddfa5bb0fc3dcad78534e70  src/pcobra/cobra/core/lexer.py
3017fa31e1707ca82358d548e71ba27d4b8e73342950ab6959b32c13dcc02505  src/pcobra/cobra/core/parser.py
fbd130d88ec6255c1e966752730a7cb2e2311c50125d85df487fc67d55aaf61e  src/pcobra/core/lexer.py
656d9c911ab0760435efc48502625b6016955f00d0429228a0ffced87e982a2b  src/pcobra/core/parser.py
```

La repetición final produce los mismos cuatro hashes: **identidad byte a
byte**. `git diff --name-only BASE_SHA..HEAD` confirma que no se modificaron
Lexer, Parser, snapshots canónicos de Lexer/Parser, gramática, intérprete,
sandbox, red, compresión, ejecución segura de procesos ni validator worker.
Tampoco se modificó sintaxis Cobra.

Los artefactos sensibles explícitamente no modificados son:

- los cuatro Lexer/Parser enumerados arriba;
- cualquier snapshot de Lexer/Parser y cualquier archivo de gramática;
- `interpreter.py` y componentes de sandbox;
- módulos de red, compresión o ejecución segura de procesos;
- cualquier validator worker;
- `docs/LIBRO_PROGRAMACION_COBRA.md`;
- workflows de GitHub.

## Lista completa de archivos modificados desde `BASE_SHA`

1. `.github/codeql/custom/ast-no-type-validation.ql`
2. `.github/codeql/custom/test/ast_no_type_validation/insecure/ast-no-type-validation.expected`
3. `.github/codeql/custom/test/ast_no_type_validation/insecure/ast-no-type-validation.qlref`
4. `.github/codeql/custom/test/ast_no_type_validation/insecure/insecure_type_validation.py`
5. `.github/codeql/custom/test/ast_no_type_validation/safe/ast-no-type-validation.expected`
6. `.github/codeql/custom/test/ast_no_type_validation/safe/ast-no-type-validation.qlref`
7. `.github/codeql/custom/test/ast_no_type_validation/safe/safe_type_validation.py`
8. `src/pcobra/cobra/transpilers/runtime_api_parity_snapshot.json`
9. `src/pcobra/corelibs/__init__.py`
10. `tests/unit/test_runtime_api_matrix_contract.py`
11. `docs/auditorias/3481_runtime_contract_y_codeql_2026-08-15/README.md`

`docs/_generated/runtime_api_matrix.json` y `.md` no figuran: el generador
validó antes de escribir y no los alteró. Por tanto, su diff contiene cero
cambios manuales, formateos o limpiezas colaterales; cuando se resuelva el
bloqueo independiente deberán actualizarse exclusivamente mediante el
generador.

## Comandos ejecutados, códigos y fragmentos

```console
$ sha256sum src/pcobra/cobra/core/{lexer.py,parser.py} src/pcobra/core/{lexer.py,parser.py}
[los cuatro hashes de la sección anterior]
[exit 0]

$ python scripts/generar_matriz_api_runtime.py
RuntimeError: Snapshot inválido para python.corelibs: símbolos desconocidos ['obtener_url_texto']
[exit 1; bloqueo nuevo independiente]

$ python scripts/validate_runtime_contract.py
ContractValidationError: cobra.system.ejecutar_comando_async.python: marcado full pero no aparece en runtime_api_matrix.available_api_by_backend.global
[exit 1; FAIL preexistente derivado]

$ python -m pytest -q tests/unit/test_runtime_api_matrix_contract.py
1 failed, 4 passed in 0.67s
[exit 1; bloqueo independiente]

$ python -m pytest -q tests/unit/test_corelibs_configuracion.py tests/unit/test_corelibs_pruebas.py tests/unit/test_corelibs_sistema.py
28 passed, 1 skipped in 0.95s
[exit 0; PASS]

$ python -m pytest -q tests/unit/test_usar_core_all_exports.py tests/test_usar_public_exports_snapshot.py tests/cli/test_runtime_imports_contract.py tests/integration/test_usar_runtime_contract.py
27 passed in 1.61s
[exit 0; PASS]

$ python -m pytest -q tests/test_codeql_config.py tests/unit/test_codeql_triggers.py
7 passed in 0.22s
[exit 0; PASS]

$ command -v codeql
[sin salida]
[exit 1; NOT DEMONSTRATED por CLI ausente]

$ black --check .
would reformat tests/unit/test_runtime_api_matrix_contract.py
[exit 1; FAIL atribuible inicial, corregido con black focal]

$ git diff --check
[sin salida]
[exit 0; PASS]
```

También se consultó la API pública de GitHub
`/repos/Alphonsus411/pCobra/actions/runs/{run_id}/jobs`: código 0; devolvió los
estados remotos CodeQL consignados arriba. Las verificaciones finales de Black,
diff, estado, estadísticas, nombres, hashes y revisión de sensibles se ejecutan
tras completar este informe y quedan reflejadas en el cierre del PR.
