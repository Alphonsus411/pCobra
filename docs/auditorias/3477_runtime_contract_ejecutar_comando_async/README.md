# Auditoría 3477: contrato runtime de `ejecutar_comando_async`

## Estado final

**PENDIENTE**.

La corrección focal está presente en la exportación agregada y en el snapshot Python, pero el generador se detiene por un bloqueo independiente formado por los otros trece símbolos indicados abajo. Conforme al alcance de esta auditoría, no se amplió el snapshot para esos símbolos y no se declara resuelto el contrato ni se actualizaron manualmente los artefactos generados.

## Base exacta y alcance

- Base exacta auditada: `0eb83da2310266c55de66ef839c0c32f9475dfae`.
- Rama de trabajo: `fix/contrato-extensiones-cobra`.
- Causa raíz demostrada: `ejecutar_comando_async` estaba omitido tanto del import agregado desde `sistema` como de `__all__` en `src/pcobra/corelibs/__init__.py`; a continuación, esa misma omisión quedó reflejada en las listas `global` y `corelibs` del snapshot Python `src/pcobra/cobra/transpilers/runtime_api_parity_snapshot.json`.
- Remediación focal revisada: importar y publicar `ejecutar_comando_async`, incorporarlo en las dos listas Python del snapshot y añadir una aserción focal para la API global.

## Bloqueo independiente literal

La ejecución del generador posterior a la actualización terminó con código `1` y el siguiente error literal:

```text
RuntimeError: Snapshot de API Python desactualizado para matriz de paridad. Nuevos símbolos sin mapear: ['contiene', 'ejecutar_proceso', 'falso', 'igual', 'info_registro', 'lanza_error', 'leer_configuracion', 'leer_ini', 'leer_json_serializacion', 'leer_toml', 'toml_disponible', 'unir_ruta', 'verdadero']. Símbolos removidos en Python: [].
```

Estos trece símbolos constituyen un hallazgo independiente. La remediación se detuvo: no se añadieron al snapshot, no se consideran resueltos y deben tratarse en otra auditoría.

## Artefactos derivados

`python scripts/generar_matriz_api_runtime.py` no llegó a escribir artefactos porque valida el snapshot antes de generarlos. Por tanto, el generador modificó **cero** archivos y, en particular, no modificó ningún artefacto derivado distinto de los dos permitidos:

- `docs/_generated/runtime_api_matrix.json`
- `docs/_generated/runtime_api_matrix.md`

El JSON derivado conservado no contiene todavía `ejecutar_comando_async` ni en `available_api_by_backend.python.global` ni en `available_api_by_backend.python.corelibs`; ambas consultas `jq -e` devolvieron `false` y código `1`. No se alteró el JSON a mano para ocultar el bloqueo.

## Archivos modificados contra la base

1. `src/pcobra/corelibs/__init__.py`: import y `__all__` agregados.
2. `src/pcobra/cobra/transpilers/runtime_api_parity_snapshot.json`: entradas Python `global` y `corelibs`.
3. `tests/unit/test_runtime_api_matrix_contract.py`: prueba focal, además normalizada con Black.
4. `docs/auditorias/3477_runtime_contract_ejecutar_comando_async/README.md`: esta evidencia.

No se modificaron Lexer, Parser, AST, gramática, `constant_folder`, `interpreter.py`, componentes de seguridad/runtime ni workflows no relacionados.

## Comandos, códigos de salida y resultados

### Error anterior en la base

Se creó un worktree temporal detached en la base exacta y se ejecutó:

```console
$ python scripts/generar_matriz_api_runtime.py
RuntimeError: Snapshot de API Python desactualizado para matriz de paridad. Nuevos símbolos sin mapear: ['contiene', 'ejecutar_proceso', 'falso', 'igual', 'info_registro', 'lanza_error', 'leer_configuracion', 'leer_ini', 'leer_json_serializacion', 'leer_toml', 'toml_disponible', 'unir_ruta', 'verdadero']. Símbolos removidos en Python: [].
[exit 1]
```

La omisión focal era coherente entre la exportación y el snapshot en esa base, por lo que esa validación de deriva no podía detectarla; la evidencia del defecto es la ausencia en ambos sitios.

### Resultado posterior y verificaciones en el orden solicitado

```console
$ python scripts/generar_matriz_api_runtime.py
RuntimeError: Snapshot de API Python desactualizado para matriz de paridad. Nuevos símbolos sin mapear: ['contiene', 'ejecutar_proceso', 'falso', 'igual', 'info_registro', 'lanza_error', 'leer_configuracion', 'leer_ini', 'leer_json_serializacion', 'leer_toml', 'toml_disponible', 'unir_ruta', 'verdadero']. Símbolos removidos en Python: [].
[exit 1]

$ python scripts/validate_runtime_contract.py
pcobra.cobra.stdlib_contract.validator.ContractValidationError: cobra.system.ejecutar_comando_async.python: marcado full pero no aparece en runtime_api_matrix.available_api_by_backend.global
[exit 1]

$ python -m pytest tests/unit/test_runtime_api_matrix_contract.py
collected 4 items
tests/unit/test_runtime_api_matrix_contract.py FF.. [100%]
FAILED test_runtime_api_snapshot_contract_is_up_to_date: bloqueo literal de los trece símbolos
FAILED test_runtime_api_matrix_has_all_official_backends_and_python_full: la lista contiene 13 elementos
2 failed, 2 passed in 0.63s
[exit 1]

$ python -m pytest tests/unit/test_corelibs_sistema.py tests/unit/test_usar_core_all_exports.py tests/test_usar_public_exports_snapshot.py
collected 20 items
19 passed, 1 skipped in 1.15s
[exit 0]

$ black --check src/pcobra/corelibs/__init__.py tests/unit/test_runtime_api_matrix_contract.py
would reformat tests/unit/test_runtime_api_matrix_contract.py
1 file would be reformatted, 1 file would be left unchanged.
[exit 1]

$ black tests/unit/test_runtime_api_matrix_contract.py
1 file reformatted.
[exit 0]

$ git diff --check
[exit 0]

$ jq -e '.available_api_by_backend.python.global | index("ejecutar_comando_async") != null' docs/_generated/runtime_api_matrix.json
false
[exit 1]

$ jq -e '.available_api_by_backend.python.corelibs | index("ejecutar_comando_async") != null' docs/_generated/runtime_api_matrix.json
false
[exit 1]
```

La primera comprobación de Black falló realmente y se corrigió el formato; debe repetirse en la revisión final. Los fallos contractuales permanecen como **FAIL**, no como advertencias.

### Repetición final de formato y control del diff

```console
$ black --check src/pcobra/corelibs/__init__.py tests/unit/test_runtime_api_matrix_contract.py
All done! ✨ 🍰 ✨
2 files would be left unchanged.
[exit 0]

$ git diff --check
[exit 0]

$ git diff --name-only 0eb83da2310266c55de66ef839c0c32f9475dfae | rg -i '(^|/)(lexer|parser|ast|grammar|gramatica|constant_folder|interpreter)(\\.|/)|(^|/)\\.github/workflows/|seguridad|security|runtime/'
[sin salida: no se encontró ninguna ruta prohibida]
[exit 1 de rg por ausencia de coincidencias; verificación satisfactoria]

$ git status --short -- docs/_generated/runtime_api_matrix.json docs/_generated/runtime_api_matrix.md
[sin salida: ninguno de los dos artefactos fue modificado]
[exit 0]
```
