# Triage de los 15 fallos de Holobit y `usar` — 2026-08-20

## 1. Objetivo y alcance

Este informe reproduce y clasifica, sin corregirlos, los **15 fallos históricos** de la suite ampliada registrada en `docs/auditoria_holobit_contract_fix.md`. El análisis relaciona cada nodo de prueba con el código productivo observado y lo contrasta con la fuente normativa `docs/LIBRO_PROGRAMACION_COBRA.md`, las políticas de `usar`, `PUBLIC_API_HOLOBIT`, los `__all__` y la matriz oficial de backends.

El cambio es exclusivamente documental. No se modifican código productivo, pruebas, Lexer, Parser, AST, transpiladores, runtime, políticas, corelibs ni contratos existentes.

## 2. Método de reproducción

Se ejecutó literalmente, desde la raíz del repositorio y sin alterar la selección de nodos, el comando de suite ampliada registrado en `docs/auditoria_holobit_contract_fix.md`. La primera ejecución produjo:

```text
15 failed, 506 passed, 5 skipped, 2 warnings in 16.35s
```

La salida íntegra de pytest, incluidos los bloques completos de los 15 fallos, se conserva en el [Apéndice A](#apéndice-a-salida-completa-de-la-primera-ejecución).

## 3. Fuentes contractuales contrastadas

1. **Libro normativo.** `docs/LIBRO_PROGRAMACION_COBRA.md` define `usar` con cadena, importación plana, rutas lógicas punteadas para módulos de proyecto, el contrato estricto del REPL y la biblioteca pública `holobit` de nueve funciones.
2. **Backends oficiales.** El Libro y `pcobra.cobra.architecture.backend_policy.PUBLIC_BACKENDS` limitan la superficie pública a `python`, `javascript` y `rust`. `OFFICIAL_TARGETS` debe coincidir exactamente con esa tupla.
3. **Holobit público.** `pcobra.corelibs.holobit.PUBLIC_API_HOLOBIT` y `pcobra.standard_library.holobit.PUBLIC_API_HOLOBIT` contienen las mismas nueve funciones, y sus `__all__` se derivan o validan contra ese contrato. `holobit_sdk` y la clase `Holobit` no pertenecen a la API pública Cobra.
4. **Política de `usar`.** `EQUIVALENCIAS_PROHIBIDAS_A_CANONICAS` asocia nombres backend con equivalentes Cobra; la precedencia de `NOMBRES_BLOQUEADOS_USAR` determina hoy un código distinto para cinco nombres. El loader separa el catálogo oficial de la resolución segura de módulos Cobra de proyecto.
5. **Matriz de compatibilidad.** La matriz pública sólo contiene los tres backends oficiales. Python tiene paridad Holobit `full`; JavaScript y Rust tienen Holobit `partial`. Rust sí declara `corelibs` y `standard_library` como `full`, lo cual no equivale a paridad completa con `holobit_sdk`.

## 4. Resumen ejecutivo por causa raíz

| Grupo | Causa raíz | Casos | Naturaleza del hallazgo |
|---|---|---:|---|
| A | Fachada histórica `pcobra.core.holobits` no saneada y colisión función/submódulo | 1, 2, 5 | Desalineación productiva de una superficie legacy respecto de la API Cobra canónica |
| B | Pruebas legacy mezclan backends retirados y paridad SDK con features generales | 3, 4, 6 | Expectativas de prueba incompatibles con el Libro y la matriz pública vigente |
| C | Precedencia contradictoria dentro de la política de símbolos de `usar` | 7–11 | El mapa promete equivalente Cobra, pero un bloqueo anterior devuelve otro código |
| D | Extensión esperada por las pruebas (`.co`) distinta del resolver (`.cobra`) | 12, 13 | Expectativa de prueba desalineada con el contrato productivo documentado |
| E | Errores de módulo se escapan antes de normalizarse al diagnóstico público | 14, 15 | Desalineación productiva en traducción/consistencia de errores de `usar` |

## 5. Tabla de triage de los 15 fallos

| # | Nodo de prueba | Código productivo involucrado | Contraste contractual | Diagnóstico / causa raíz | Acción futura sugerida (fuera de alcance) |
|---:|---|---|---|---|---|
| 1 | `test_holobit_no_fuga_exports.py::test_superficies_holobit_solo_exportan_api_canonica[pcobra.core.holobits]` | `src/pcobra/core/holobits/__init__.py`: `__all__`, `PUBLIC_API_HOLOBIT` | Corelibs y standard library exponen nueve funciones; el Libro indexa nueve | La fachada legacy añade `Holobit`, `escalar` y `mover` | Sanear o aislar la fachada legacy preservando compatibilidad donde corresponda |
| 2 | `test_holobit_no_fuga_exports.py::test_no_fuga_de_sdk_ni_clases_internas[pcobra.core.holobits-Holobit]` | `src/pcobra/core/holobits/__init__.py`: `__getattr__` y `_LEGACY_EXPORT_MODULES` | `Holobit` no está en `PUBLIC_API_HOLOBIT` Cobra ni en los `__all__` canónicos | `__getattr__` importa deliberadamente la clase legacy | Retirar la fuga de la superficie Cobra sin borrar compatibilidad interna necesaria |
| 3 | `test_holobit_sdk_fallback_contract.py::test_gap_contract_non_python_declara_no_paridad_sdk` | `compatibility_matrix.py`: `BACKEND_FEATURE_GAPS` filtrado por `PUBLIC_BACKENDS` | Únicos backends públicos: Python, JavaScript y Rust | La prueba intenta indexar `wasm`, `go`, `cpp`, `java` y `asm`; el primer `KeyError` es `wasm` | Actualizar el contrato de prueba en un hallazgo independiente; no reintroducir targets legacy públicos |
| 4 | `test_holobit_sdk_fallback_contract.py::test_fallback_contract_no_promueve_sdk_full_fuera_de_python[rust]` | `compatibility_matrix.py`: Rust declara Holobit `partial`, pero `corelibs`/`standard_library` `full` | “SDK full” sólo aplica a features Holobit; el backend oficial Rust puede tener runtime base `full` | La prueba exige que **todas** las `CONTRACT_FEATURES` sean no-`full` fuera de Python | Separar paridad SDK de compatibilidad general del runtime en la aserción contractual |
| 5 | `test_holobit_sdk_integration.py::test_graficar_usa_sdk` | Paquete `pcobra.core.holobits`, submódulo `graficar.py` y export lazy homónimo | La API Cobra pública es la función adaptada y `graficar()` devuelve estado estable | En el orden de suite, `from core.holobits import graficar` resuelve al objeto módulo; no tiene `__globals__` | Eliminar la ambigüedad función/submódulo en la fachada legacy sin tocar la API canónica |
| 6 | `test_holobit_sdk_integration.py::test_python_es_el_unico_backend_con_sdk_full` | `BACKEND_COMPATIBILITY`, `CONTRACT_FEATURES`, `OFFICIAL_TARGETS` | Sólo Python es SDK-full; Rust es `full` únicamente en features base | La prueba interpreta cualquier `full` de corelibs como “SDK full” y encuentra Rust | Comprobar exclusivamente las features Holobit o usar `SDK_FULL_BACKENDS` |
| 7 | `test_usar_loader_public_api_contract.py::test_politica_de_simbolos_prohibidos_devuelve_codigo_y_mensaje[append]` | `usar_symbol_policy.py`: `NOMBRES_BLOQUEADOS_USAR` antes de equivalencias | El mapa declara `append → agregar` | La rama temprana devuelve `explicit_forbidden_name`, no `cobra_public_equivalent` | Unificar precedencia/código sin relajar el rechazo |
| 8 | Mismo nodo parametrizado `[expect]` | Misma política; `expect → obtener_o_error` | Existe equivalente Cobra explícito | Misma precedencia contradictoria | Ídem |
| 9 | Mismo nodo parametrizado `[filter]` | Misma política; `filter → filtrar` | Existe equivalente Cobra explícito | Misma precedencia contradictoria | Ídem |
| 10 | Mismo nodo parametrizado `[map]` | Misma política; `map → mapear` | Existe equivalente Cobra explícito | Misma precedencia contradictoria | Ídem |
| 11 | Mismo nodo parametrizado `[unwrap]` | Misma política; `unwrap → obtener_o_error` | Existe equivalente Cobra explícito | Misma precedencia contradictoria | Ídem |
| 12 | `test_usar_loader_validation.py::test_resolver_modulo_cobra_proyecto_convierte_nombre_punteado_en_co` | `usar_loader.py::resolver_modulo_cobra_proyecto`, que aplica `.with_suffix(".cobra")` | El Libro acepta la ruta lógica `usar "mi_modulo.utilidades"`; el resolver documenta archivo `.cobra` | La fixture sólo crea `utilidades/fechas.co`, por lo que el resolver termina en `FileNotFoundError` | Aclarar normativamente la extensión y ajustar la expectativa en un cambio independiente |
| 13 | `test_usar_loader_validation.py::test_resolver_modulo_cobra_proyecto_rechaza_traversal_por_symlink` | Mismo resolver y `_verificar_path_dentro_de_root` | La protección anti-traversal existe para la ruta candidata `.cobra` | La prueba crea `fechas.co`; nunca alcanza la comprobación del symlink y recibe `FileNotFoundError` | Alinear fixture/extensión para ejercitar realmente el control de seguridad |
| 14 | `test_usar_public_contract.py::test_usar_modulo_inexistente_falla_con_diagnostico_publico` | Flujo REPL/loader y mensaje de módulo externo | El REPL debe abortar antes de imports externos con error público, sin estado parcial | Hay `PermissionError`, pero el texto carece del código estructurado `usar_error[...]` exigido por el nodo | Centralizar traducción a diagnóstico público manteniendo atomicidad |
| 15 | `test_usar_public_contract.py::test_rechaza_usar_ruta_backend_no_canonica_con_error_consistente` | `validar_nombre_modulo_usar` llamado desde `usar_modulo`/intérprete | Las rutas backend directas no pertenecen a `usar`; deben rechazarse consistentemente | La validación sintáctica lanza `ValueError` antes de la traducción esperada a `PermissionError`/`FileNotFoundError` | Normalizar el error en la frontera pública del intérprete/loader |

## 6. Confirmaciones explícitas del contrato vigente

- **`graficar()` devuelve `{"estado": "ok"}`.** La implementación pública de `pcobra.corelibs.holobit.graficar` invoca el adaptador, valida una salida JSON estable y retorna exactamente ese diccionario.
- **Los valores no finitos se rechazan.** `_normalizar_valores` convierte cada número una vez, aplica `math.isfinite` y lanza `ValueError("Todos los valores del holobit deben ser finitos")` para `NaN`, `Infinity` y `-Infinity`.
- **`holobit_sdk` no es API pública Cobra.** No forma parte de `PUBLIC_API_HOLOBIT` ni de los `__all__` canónicos de corelibs/standard library; además, la política de `usar` lo bloquea y ofrece `crear_holobit` como equivalente público.
- **Los únicos backends públicos oficiales son `python`, `javascript` y `rust`.** Así lo fijan el Libro, `PUBLIC_BACKENDS`, `OFFICIAL_TARGETS` y la matriz pública filtrada.

## 7. Decisión de alcance

No se modifica ningún fallo en esta tarea: agruparlos revela cinco causas raíz que requieren hallazgos incrementales separados. Resolverlos juntos mezclaría saneamiento de una fachada legacy, semántica de matriz, precedencia de políticas, extensión de módulos y traducción de errores, en contra de la regla de auditoría “uno por uno”. En particular, no es necesario ni está autorizado tocar Lexer o Parser para este triage.

## 8. Verificaciones finales

Al final de la tarea se repite literalmente la suite ampliada y se ejecuta el archivo unitario del adaptador Holobit. También se comprueban `git diff --check`, `git status --short`, el diff final y la ausencia de cambios en Lexer, Parser, AST, transpiladores, runtime, políticas, corelibs y tests. Resultados observados:

- Suite ampliada final: `15 failed, 506 passed, 5 skipped, 2 warnings in 14.66s`; reproduce los mismos 15 nodos del baseline.
- Adaptador Holobit: `32 passed in 1.88s`.
- `git diff --check`: sin errores.
- La inspección de rutas modificadas sólo muestra este README documental; por tanto, no hay cambios en Lexer, Parser, AST, transpiladores, runtime, políticas, corelibs ni tests.

## Apéndice A. Salida completa de la primera ejecución

La siguiente transcripción conserva la salida completa emitida por pytest, incluida la salida completa de cada uno de los 15 fallos:

```text
........................................................................ [ 13%]
............................................................F....F...... [ 27%]
..................................................sssssF..FF....F....... [ 41%]
........................................................................ [ 54%]
........................................................................ [ 68%]
................................................................FFFF.F.. [ 82%]
.................F................F..................................... [ 95%]
..........F........F..                                                   [100%]
=================================== FAILURES ===================================
__ test_superficies_holobit_solo_exportan_api_canonica[pcobra.core.holobits] ___
tests/unit/test_holobit_no_fuga_exports.py:35: in test_superficies_holobit_solo_exportan_api_canonica
    assert set(mod.__all__) == EXPECTED_API
E   AssertionError: assert {'Holobit', '...raficar', ...} == {'combinar', ...oyectar', ...}
E
E     Extra items in the left set:
E     'mover'
E     'escalar'
E     'Holobit'
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
____ test_politica_de_simbolos_prohibidos_devuelve_codigo_y_mensaje[append] ____
tests/unit/test_usar_loader_public_api_contract.py:143: in test_politica_de_simbolos_prohibidos_devuelve_codigo_y_mensaje
    assert resultado.codigo == "cobra_public_equivalent"
E   AssertionError: assert 'explicit_forbidden_name' == 'cobra_public_equivalent'
E
E     - cobra_public_equivalent
E     + explicit_forbidden_name
____ test_politica_de_simbolos_prohibidos_devuelve_codigo_y_mensaje[expect] ____
tests/unit/test_usar_loader_public_api_contract.py:143: in test_politica_de_simbolos_prohibidos_devuelve_codigo_y_mensaje
    assert resultado.codigo == "cobra_public_equivalent"
E   AssertionError: assert 'explicit_forbidden_name' == 'cobra_public_equivalent'
E
E     - cobra_public_equivalent
E     + explicit_forbidden_name
____ test_politica_de_simbolos_prohibidos_devuelve_codigo_y_mensaje[filter] ____
tests/unit/test_usar_loader_public_api_contract.py:143: in test_politica_de_simbolos_prohibidos_devuelve_codigo_y_mensaje
    assert resultado.codigo == "cobra_public_equivalent"
E   AssertionError: assert 'explicit_forbidden_name' == 'cobra_public_equivalent'
E
E     - cobra_public_equivalent
E     + explicit_forbidden_name
_____ test_politica_de_simbolos_prohibidos_devuelve_codigo_y_mensaje[map] ______
tests/unit/test_usar_loader_public_api_contract.py:143: in test_politica_de_simbolos_prohibidos_devuelve_codigo_y_mensaje
    assert resultado.codigo == "cobra_public_equivalent"
E   AssertionError: assert 'explicit_forbidden_name' == 'cobra_public_equivalent'
E
E     - cobra_public_equivalent
E     + explicit_forbidden_name
____ test_politica_de_simbolos_prohibidos_devuelve_codigo_y_mensaje[unwrap] ____
tests/unit/test_usar_loader_public_api_contract.py:143: in test_politica_de_simbolos_prohibidos_devuelve_codigo_y_mensaje
    assert resultado.codigo == "cobra_public_equivalent"
E   AssertionError: assert 'explicit_forbidden_name' == 'cobra_public_equivalent'
E
E     - cobra_public_equivalent
E     + explicit_forbidden_name
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
__________ test_usar_modulo_inexistente_falla_con_diagnostico_publico __________
tests/unit/test_usar_public_contract.py:136: in test_usar_modulo_inexistente_falla_con_diagnostico_publico
    assert "modulo_fuera_catalogo_publico" in mensaje or "usar_error[" in mensaje
E   assert ('modulo_fuera_catalogo_publico' in "importación no permitida en 'usar': 'modulo_inexistente'. es un módulo backend/no canónico y no forma parte de la api pública. módulos permitidos: numero, texto, datos, logica, asincrono, sistema, archivo, tiempo, red, holobit." or 'usar_error[' in "importación no permitida en 'usar': 'modulo_inexistente'. es un módulo backend/no canónico y no forma parte de la api pública. módulos permitidos: numero, texto, datos, logica, asincrono, sistema, archivo, tiempo, red, holobit.")
_______ test_rechaza_usar_ruta_backend_no_canonica_con_error_consistente _______
tests/unit/test_usar_public_contract.py:243: in test_rechaza_usar_ruta_backend_no_canonica_con_error_consistente
    interp.ejecutar_usar(_NodoUsar())
src/pcobra/core/interpreter.py:2823: in ejecutar_usar
    exports = _usar_modulo_con_estado_aislado(
src/pcobra/core/interpreter.py:135: in _usar_modulo_con_estado_aislado
    return usar_modulo(nombre, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/pcobra/cobra/usar_loader.py:1057: in usar_modulo
    validar_nombre_modulo_usar(nombre_raw, require_allowlist=True)
src/pcobra/cobra/usar_loader.py:273: in validar_nombre_modulo_usar
    raise ValueError(f"Nombre de módulo '{nombre}' no es seguro para 'usar'.")
E   ValueError: Nombre de módulo 'pcobra.corelibs.numero' no es seguro para 'usar'.
=============================== warnings summary ===============================
tests/integration/test_repl_usar_entrypoints_contract.py::test_repl_contract_pipeline_completo_por_modulo_canonico[asincrono]
  /workspace/pCobra/tests/integration/test_repl_usar_entrypoints_contract.py:1483: DeprecationWarning: There is no current event loop
    interp.contextos[-1].values[symbol](asyncio.Future())

tests/integration/test_repl_usar_entrypoints_contract.py::test_repl_contract_colision_warn_alias_required_estructurada
  /workspace/pCobra/src/pcobra/core/interpreter.py:2832: RuntimeWarning: Conflicto de nombres en `usar`: el símbolo 'es_finito' ya existe y no será sobrescrito.
    self._inyectar_exports_modulo_proyecto(exports)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
============================= slowest 10 durations =============================
4.48s call     tests/integration/test_usar_canonical_surface_contract.py::test_caso_9_startup_runtime_y_cli_no_cargan_backends_legacy
0.33s call     tests/integration/test_repl_usar_entrypoints_contract.py::test_repl_usar_modulos_numero_logica_tiempo_y_datos_con_epoch_rango
0.28s call     tests/integration/test_repl_usar_entrypoints_contract.py::test_repl_contrato_cli_superficie_publica_y_error_corto_numpy
0.28s call     tests/integration/test_repl_usar_entrypoints_contract.py::test_repl_integracion_usar_modulos_publicos_end_to_end[<lambda>-<lambda>-<lambda>]
0.24s call     tests/integration/test_repl_usar_entrypoints_contract.py::test_repl_integracion_usar_modulos_publicos_end_to_end[ReplCommandV2-<lambda>-<lambda>]
0.17s call     tests/unit/test_usar_public_contract.py::test_runtime_startup_no_carga_legacy_backends
0.12s call     tests/integration/test_repl_usar_entrypoints_contract.py::test_repl_usar_datos_numero_archivo_contrato_basico_sin_errores_metadata
0.12s call     tests/integration/test_usar_canonical_surface_contract.py::test_usar_reimportes_reinyecciones_metadata_canonica_e_idempotente[<lambda>]
0.10s call     tests/integration/test_usar_canonical_surface_contract.py::test_usar_reimportes_reinyecciones_metadata_canonica_e_idempotente[ReplCommandV2]
0.09s call     tests/integration/test_repl_usar_entrypoints_contract.py::test_interprete_corelibs_superficie_minima_requerida
=========================== short test summary info ============================
FAILED tests/unit/test_holobit_no_fuga_exports.py::test_superficies_holobit_solo_exportan_api_canonica[pcobra.core.holobits]
FAILED tests/unit/test_holobit_no_fuga_exports.py::test_no_fuga_de_sdk_ni_clases_internas[pcobra.core.holobits-Holobit]
FAILED tests/unit/test_holobit_sdk_fallback_contract.py::test_gap_contract_non_python_declara_no_paridad_sdk
FAILED tests/unit/test_holobit_sdk_fallback_contract.py::test_fallback_contract_no_promueve_sdk_full_fuera_de_python[rust]
FAILED tests/unit/test_holobit_sdk_integration.py::test_graficar_usa_sdk - At...
FAILED tests/unit/test_holobit_sdk_integration.py::test_python_es_el_unico_backend_con_sdk_full
FAILED tests/unit/test_usar_loader_public_api_contract.py::test_politica_de_simbolos_prohibidos_devuelve_codigo_y_mensaje[append]
FAILED tests/unit/test_usar_loader_public_api_contract.py::test_politica_de_simbolos_prohibidos_devuelve_codigo_y_mensaje[expect]
FAILED tests/unit/test_usar_loader_public_api_contract.py::test_politica_de_simbolos_prohibidos_devuelve_codigo_y_mensaje[filter]
FAILED tests/unit/test_usar_loader_public_api_contract.py::test_politica_de_simbolos_prohibidos_devuelve_codigo_y_mensaje[map]
FAILED tests/unit/test_usar_loader_public_api_contract.py::test_politica_de_simbolos_prohibidos_devuelve_codigo_y_mensaje[unwrap]
FAILED tests/unit/test_usar_loader_validation.py::test_resolver_modulo_cobra_proyecto_convierte_nombre_punteado_en_co
FAILED tests/unit/test_usar_loader_validation.py::test_resolver_modulo_cobra_proyecto_rechaza_traversal_por_symlink
FAILED tests/unit/test_usar_public_contract.py::test_usar_modulo_inexistente_falla_con_diagnostico_publico
FAILED tests/unit/test_usar_public_contract.py::test_rechaza_usar_ruta_backend_no_canonica_con_error_consistente
15 failed, 506 passed, 5 skipped, 2 warnings in 16.35s
```
