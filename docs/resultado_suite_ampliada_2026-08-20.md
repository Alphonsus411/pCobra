# Resultado de la suite ampliada documentada

## Contexto

- Fecha de ejecución: 2026-08-20.
- Directorio de ejecución: `/workspace/pCobra`.
- Selección: los 26 archivos registrados bajo «Suite ampliada documentada» en
  `docs/auditoria_holobit_contract_fix.md`, sin alterar el orden.
- Resultado esperado para preparar el cierre: `8 failed, 513 passed, 5 skipped`.
- Resultado obtenido: `19 failed, 502 passed, 5 skipped, 2 warnings in 14.06s`.
- Decisión: se detiene la preparación del cierre porque el número de fallos no
  es ocho. La discrepancia debe diagnosticarse por separado.

## Comando ejecutado

```console
$ pytest -q tests/integration/test_holobit_tiers.py tests/integration/transpilers/test_holobit_hooks_golden.py tests/unit/test_corelibs_holobit_adapter.py tests/unit/test_holobit_backend_contract_matrix.py tests/unit/test_holobit_corelib_domain_errors.py tests/unit/test_holobit_generation.py tests/unit/test_holobit_graficar_contract.py tests/unit/test_holobit_no_fuga_exports.py tests/unit/test_holobit_runtime_backends.py tests/unit/test_holobit_sdk_compatibility_report.py tests/unit/test_holobit_sdk_fallback_contract.py tests/unit/test_holobit_sdk_integration.py tests/unit/test_holobit_transformacion_extra.py tests/unit/test_parser_holobit.py tests/unit/test_to_js_holobit_runtime_snapshot.py tests/integration/test_repl_usar_entrypoints_contract.py tests/integration/test_usar_canonical_surface_contract.py tests/integration/test_usar_core_contract_full.py tests/integration/test_usar_export_sanitation.py tests/integration/test_usar_public_contract_regression.py tests/integration/test_usar_runtime_contract.py tests/unit/test_usar_loader_public_api_contract.py tests/unit/test_usar_loader_validation.py tests/unit/test_usar_numpy_error_contract.py tests/unit/test_usar_policy_contract.py tests/unit/test_usar_public_contract.py
```

## Salida completa

```text
........................................................................ [ 13%]
............................................................F....F...... [ 27%]
..................................................sssssF..FF....F....... [ 41%]
..........................F..FFFF............F.......................... [ 54%]
..........................F.......................................F..... [ 68%]
........................................................................ [ 82%]
.................F................F..........FFF........................ [ 95%]
......................                                                   [100%]
=================================== FAILURES ===================================
__ test_superficies_holobit_solo_exportan_api_canonica[pcobra.core.holobits] ___
tests/unit/test_holobit_no_fuga_exports.py:35: in test_superficies_holobit_solo_exportan_api_canonica
    assert set(mod.__all__) == EXPECTED_API
E   AssertionError: assert {'Holobit', '...raficar', ...} == {'combinar', ...oyectar', ...}
E     
E     Extra items in the left set:
E     'escalar'
E     'Holobit'
E     'mover'
E     Use -v to get more diff
_____ test_no_fuga_de_sdk_ni_clases_internas[pcobra.core.holobits-Holobit] _____
tests/unit/test_holobit_no_fuga_exports.py:54: in test_no_fuga_de_sdk_ni_clases_internas
    with pytest.raises(AttributeError):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   Failed: DID NOT RAISE <class 'AttributeError'>
_____________ test_gap_contract_non_python_declara_no_paridad_sdk ______________
tests/unit/test_holobit_sdk_fallback_contract.py:74: in test_gap_contract_non_python_declara_no_paridad_sdk
    assert len(BACKEND_FEATURE_GAPS[backend]["holobit"]) >= 1
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   KeyError: 'wasm'
______ test_fallback_contract_no_promueve_sdk_full_fuera_de_python[rust] _______
tests/unit/test_holobit_sdk_fallback_contract.py:85: in test_fallback_contract_no_promueve_sdk_full_fuera_de_python
    assert BACKEND_COMPATIBILITY[backend][feature] != "full"
E   AssertionError: assert 'full' != 'full'
____________________________ test_graficar_usa_sdk _____________________________
tests/unit/test_holobit_sdk_integration.py:20: in test_graficar_usa_sdk
    monkeypatch.setitem(graficar.__globals__, "_HOLOBIT_SDK_ERROR", None)
                        ^^^^^^^^^^^^^^^^^^^^
E   AttributeError: module 'pcobra.core.holobits.graficar' has no attribute '__globals__'
_________________ test_python_es_el_unico_backend_con_sdk_full _________________
tests/unit/test_holobit_sdk_integration.py:72: in test_python_es_el_unico_backend_con_sdk_full
    assert full_backends == {"python"}
E   AssertionError: assert {'python', 'rust'} == {'python'}
E     
E     Extra items in the left set:
E     'rust'
E     Use -v to get more diff
_______ test_seguridad_usar_numpy_error_corto_sin_traceback_modo_normal ________
tests/integration/test_repl_usar_entrypoints_contract.py:598: in test_seguridad_usar_numpy_error_corto_sin_traceback_modo_normal
    assert (
E   assert "Importación no permitida en 'usar': 'numpy'. Es un módulo backend/no canónico y no forma parte de la API pública." in "usar_error[modulo_fuera_catalogo_publico]: No se puede usar 'numpy': módulo fuera del catálogo público."
_ test_repl_seguridad_numpy_rechazado_mensaje_corto_sin_traceback[<lambda>-<lambda>] _
tests/integration/test_repl_usar_entrypoints_contract.py:680: in test_repl_seguridad_numpy_rechazado_mensaje_corto_sin_traceback
    assert (
E   assert "Importación no permitida en 'usar': 'numpy'. Es un módulo backend/no canónico y no forma parte de la API pública." in "usar_error[modulo_fuera_catalogo_publico]: No se puede usar 'numpy': módulo fuera del catálogo público."
_ test_repl_seguridad_numpy_rechazado_mensaje_corto_sin_traceback[ReplCommandV2-<lambda>] _
tests/integration/test_repl_usar_entrypoints_contract.py:680: in test_repl_seguridad_numpy_rechazado_mensaje_corto_sin_traceback
    assert (
E   assert "Importación no permitida en 'usar': 'numpy'. Es un módulo backend/no canónico y no forma parte de la API pública." in "usar_error[modulo_fuera_catalogo_publico]: No se puede usar 'numpy': módulo fuera del catálogo público."
__________ test_repl_rechazo_numpy_es_persistente[<lambda>-<lambda>] ___________
tests/integration/test_repl_usar_entrypoints_contract.py:703: in test_repl_rechazo_numpy_es_persistente
    assert (
E   assert "Importación no permitida en 'usar': 'numpy'. Es un módulo backend/no canónico y no forma parte de la API pública." in "usar_error[modulo_fuera_catalogo_publico]: No se puede usar 'numpy': módulo fuera del catálogo público."
________ test_repl_rechazo_numpy_es_persistente[ReplCommandV2-<lambda>] ________
tests/integration/test_repl_usar_entrypoints_contract.py:703: in test_repl_rechazo_numpy_es_persistente
    assert (
E   assert "Importación no permitida en 'usar': 'numpy'. Es un módulo backend/no canónico y no forma parte de la API pública." in "usar_error[modulo_fuera_catalogo_publico]: No se puede usar 'numpy': módulo fuera del catálogo público."
___ test_repl_contract_seguridad_usar_atomico_holobit_y_datos_sin_overwrite ____
tests/integration/test_repl_usar_entrypoints_contract.py:1056: in test_repl_contract_seguridad_usar_atomico_holobit_y_datos_sin_overwrite
    assert "'code': 'symbol_collision'" in mensaje_holobit
E   assert "'code': 'symbol_collision'" in "usar_error[conflicto_simbolo]: No se puede usar 'holobit': hay conflicto de símbolos en el contexto actual."
___ test_repl_usar_numpy_error_explicito_corto_sin_traceback_en_modo_normal ____
tests/integration/test_repl_usar_entrypoints_contract.py:2109: in test_repl_usar_numpy_error_explicito_corto_sin_traceback_en_modo_normal
    assert (
E   assert "Importación no permitida en 'usar': 'numpy'. Es un módulo backend/no canónico y no forma parte de la API pública. Módulos permitidos: numero, texto, datos, logica, asincrono, sistema, archivo, tiempo, red, holobit." in "usar_error[modulo_fuera_catalogo_publico]: No se puede usar 'numpy': módulo fuera del catálogo público."
_________________ test_09_colision_reporta_error_estructurado __________________
tests/integration/test_usar_core_contract_full.py:198: in test_09_colision_reporta_error_estructurado
    detalle = _extraer_error_estructurado_desde_colision(str(excinfo.value))
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/integration/test_usar_core_contract_full.py:37: in _extraer_error_estructurado_desde_colision
    assert prefijo in mensaje
E   assert 'colisión estructurada=' in "usar_error[conflicto_simbolo]: No se puede usar 'datos': hay conflicto de símbolos en el contexto actual."
_____ test_resolver_modulo_cobra_proyecto_convierte_nombre_punteado_en_co ______
tests/unit/test_usar_loader_validation.py:91: in test_resolver_modulo_cobra_proyecto_convierte_nombre_punteado_en_co
    ruta = resolver_modulo_cobra_proyecto("utilidades.fechas", project_root=tmp_path)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/pcobra/cobra/usar_loader.py:396: in resolver_modulo_cobra_proyecto
    raise FileNotFoundError(f"Módulo no encontrado: {nombre}")
E   FileNotFoundError: Módulo no encontrado: utilidades.fechas
______ test_resolver_modulo_cobra_proyecto_rechaza_traversal_por_symlink _______
tests/unit/test_usar_loader_validation.py:133: in test_resolver_modulo_cobra_proyecto_rechaza_traversal_por_symlink
    resolver_modulo_cobra_proyecto("utilidades.fechas", project_root=tmp_path)
src/pcobra/cobra/usar_loader.py:396: in resolver_modulo_cobra_proyecto
    raise FileNotFoundError(f"Módulo no encontrado: {nombre}")
E   FileNotFoundError: Módulo no encontrado: utilidades.fechas
_________ test_usar_numpy_rechaza_con_error_corto_sin_detalle_tecnico __________
tests/unit/test_usar_numpy_error_contract.py:20: in test_usar_numpy_rechaza_con_error_corto_sin_detalle_tecnico
    assert (
E   AssertionError: assert 'usar_error[m...logo público.' == 'No se puede ...logo público.'
E     
E     - No se puede usar 'numpy': módulo fuera del catálogo público.
E     + usar_error[modulo_fuera_catalogo_publico]: No se puede usar 'numpy': módulo fuera del catálogo público.
___________ test_usar_numpy_no_filtra_detalle_tecnico_en_log_normal ____________
tests/unit/test_usar_numpy_error_contract.py:35: in test_usar_numpy_no_filtra_detalle_tecnico_en_log_normal
    assert "usar_error[" not in mensajes
E   AssertionError: assert 'usar_error[' not in 'Token ident...ogo público.'
E     
E     'usar_error[' is contained here:
E       lo numpy: usar_error[modulo_fuera_catalogo_publico]: No se puede usar 'numpy': módulo fuera del catálogo público.
E     ?           +++++++++++
------------------------------ Captured log call -------------------------------
DEBUG    pcobra.cobra.core.lexer:lexer.py:464 Token identificado: TipoToken.USAR, valor: 'usar', posición: 0
DEBUG    pcobra.cobra.core.lexer:lexer.py:464 Token identificado: TipoToken.CADENA, valor: 'numpy', posición: 5
DEBUG    root:interpreter.py:2886 Error esperado al usar módulo numpy: usar_error[modulo_fuera_catalogo_publico]: No se puede usar 'numpy': módulo fuera del catálogo público.
____________ test_usar_numpy_incluye_detalle_tecnico_solo_con_debug ____________
tests/unit/test_usar_numpy_error_contract.py:47: in test_usar_numpy_incluye_detalle_tecnico_solo_con_debug
    assert mensaje.startswith(
E   assert False
E    +  where False = <built-in method startswith of str object at 0x7fd896d10490>("No se puede usar 'numpy': módulo fuera del catálogo público.")
E    +    where <built-in method startswith of str object at 0x7fd896d10490> = "usar_error[modulo_fuera_catalogo_publico]: No se puede usar 'numpy': módulo fuera del catálogo público.".startswith
------------------------------ Captured log call -------------------------------
ERROR    root:interpreter.py:2882 Error al usar el módulo 'numpy': usar_error[modulo_fuera_catalogo_publico]: No se puede usar 'numpy': módulo fuera del catálogo público.
Traceback (most recent call last):
  File "/workspace/pCobra/src/pcobra/core/interpreter.py", line 2824, in ejecutar_usar
    exports = _usar_modulo_con_estado_aislado(
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/pCobra/src/pcobra/core/interpreter.py", line 135, in _usar_modulo_con_estado_aislado
    return usar_modulo(nombre, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/pCobra/src/pcobra/cobra/usar_loader.py", line 998, in usar_modulo
    raise permiso_exc
  File "/workspace/pCobra/src/pcobra/cobra/usar_loader.py", line 969, in usar_modulo
    nombre_validado_oficial = validar_nombre_modulo_usar(
                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/pCobra/src/pcobra/cobra/usar_loader.py", line 263, in validar_nombre_modulo_usar
    _rechazar_modulo_no_canonico(nombre_raw)
  File "/workspace/pCobra/src/pcobra/cobra/usar_loader.py", line 239, in _rechazar_modulo_no_canonico
    raise ModuloFueraCatalogoPublicoError(mensaje_error_no_canonico)
pcobra.cobra.usar_loader.ModuloFueraCatalogoPublicoError: Importación no permitida en 'usar': 'numpy'. Es un módulo backend/no canónico y no forma parte de la API pública. usar_error[modulo_fuera_catalogo_publico]: módulo fuera del catálogo público. módulo externo no permitido en REPL estricto (solo alias oficiales Cobra). Módulos permitidos: numero, texto, datos, logica, asincrono, sistema, archivo, tiempo, red, holobit, ruta, serializacion, proceso, registro, argumentos, pruebas, temporal, cripto, regex, compresion, configuracion.
=============================== warnings summary ===============================
tests/integration/test_repl_usar_entrypoints_contract.py::test_repl_contract_pipeline_completo_por_modulo_canonico[asincrono]
  /workspace/pCobra/tests/integration/test_repl_usar_entrypoints_contract.py:1483: DeprecationWarning: There is no current event loop
    interp.contextos[-1].values[symbol](asyncio.Future())

tests/integration/test_repl_usar_entrypoints_contract.py::test_repl_contract_colision_warn_alias_required_estructurada
  /workspace/pCobra/src/pcobra/core/interpreter.py:2833: RuntimeWarning: Conflicto de nombres en `usar`: el símbolo 'es_finito' ya existe y no será sobrescrito.
    self._inyectar_exports_modulo_proyecto(exports)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
============================= slowest 10 durations =============================
4.52s call     tests/integration/test_usar_canonical_surface_contract.py::test_caso_9_startup_runtime_y_cli_no_cargan_backends_legacy
0.27s call     tests/integration/test_repl_usar_entrypoints_contract.py::test_repl_usar_modulos_numero_logica_tiempo_y_datos_con_epoch_rango
0.26s call     tests/integration/test_repl_usar_entrypoints_contract.py::test_repl_contrato_cli_superficie_publica_y_error_corto_numpy
0.23s call     tests/integration/test_repl_usar_entrypoints_contract.py::test_repl_integracion_usar_modulos_publicos_end_to_end[<lambda>-<lambda>-<lambda>]
0.23s call     tests/integration/test_repl_usar_entrypoints_contract.py::test_repl_integracion_usar_modulos_publicos_end_to_end[ReplCommandV2-<lambda>-<lambda>]
0.15s call     tests/unit/test_holobit_backend_contract_matrix.py::test_codegen_contract_for_cobra_hooks_matches_matrix_level[proyectar-rust]
0.14s call     tests/unit/test_usar_public_contract.py::test_runtime_startup_no_carga_legacy_backends
0.14s call     tests/integration/test_usar_canonical_surface_contract.py::test_usar_reimportes_reinyecciones_metadata_canonica_e_idempotente[<lambda>]
0.12s call     tests/integration/test_repl_usar_entrypoints_contract.py::test_repl_usar_datos_numero_archivo_contrato_basico_sin_errores_metadata
0.11s call     tests/integration/test_usar_canonical_surface_contract.py::test_usar_reimportes_reinyecciones_metadata_canonica_e_idempotente[ReplCommandV2]
=========================== short test summary info ============================
FAILED tests/unit/test_holobit_no_fuga_exports.py::test_superficies_holobit_solo_exportan_api_canonica[pcobra.core.holobits]
FAILED tests/unit/test_holobit_no_fuga_exports.py::test_no_fuga_de_sdk_ni_clases_internas[pcobra.core.holobits-Holobit]
FAILED tests/unit/test_holobit_sdk_fallback_contract.py::test_gap_contract_non_python_declara_no_paridad_sdk
FAILED tests/unit/test_holobit_sdk_fallback_contract.py::test_fallback_contract_no_promueve_sdk_full_fuera_de_python[rust]
FAILED tests/unit/test_holobit_sdk_integration.py::test_graficar_usa_sdk - At...
FAILED tests/unit/test_holobit_sdk_integration.py::test_python_es_el_unico_backend_con_sdk_full
FAILED tests/integration/test_repl_usar_entrypoints_contract.py::test_seguridad_usar_numpy_error_corto_sin_traceback_modo_normal
FAILED tests/integration/test_repl_usar_entrypoints_contract.py::test_repl_seguridad_numpy_rechazado_mensaje_corto_sin_traceback[<lambda>-<lambda>]
FAILED tests/integration/test_repl_usar_entrypoints_contract.py::test_repl_seguridad_numpy_rechazado_mensaje_corto_sin_traceback[ReplCommandV2-<lambda>]
FAILED tests/integration/test_repl_usar_entrypoints_contract.py::test_repl_rechazo_numpy_es_persistente[<lambda>-<lambda>]
FAILED tests/integration/test_repl_usar_entrypoints_contract.py::test_repl_rechazo_numpy_es_persistente[ReplCommandV2-<lambda>]
FAILED tests/integration/test_repl_usar_entrypoints_contract.py::test_repl_contract_seguridad_usar_atomico_holobit_y_datos_sin_overwrite
FAILED tests/integration/test_repl_usar_entrypoints_contract.py::test_repl_usar_numpy_error_explicito_corto_sin_traceback_en_modo_normal
FAILED tests/integration/test_usar_core_contract_full.py::test_09_colision_reporta_error_estructurado
FAILED tests/unit/test_usar_loader_validation.py::test_resolver_modulo_cobra_proyecto_convierte_nombre_punteado_en_co
FAILED tests/unit/test_usar_loader_validation.py::test_resolver_modulo_cobra_proyecto_rechaza_traversal_por_symlink
FAILED tests/unit/test_usar_numpy_error_contract.py::test_usar_numpy_rechaza_con_error_corto_sin_detalle_tecnico
FAILED tests/unit/test_usar_numpy_error_contract.py::test_usar_numpy_no_filtra_detalle_tecnico_en_log_normal
FAILED tests/unit/test_usar_numpy_error_contract.py::test_usar_numpy_incluye_detalle_tecnico_solo_con_debug
19 failed, 502 passed, 5 skipped, 2 warnings in 14.06s
```
