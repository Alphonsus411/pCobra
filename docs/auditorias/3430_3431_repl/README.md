# Auditoría reproducible de equivalencia run/REPL (#3430/#3431)

## Referencias inmutables y entorno

- Referencia base: `242a5a6a7822889a1ae696492c72de1dd31e67b1` (merge de #3431).
- Worktree usado: `/tmp/pCobra-242a5a6a7822889a1ae696492c72de1dd31e67b1`, creado detached con `git worktree add --detach`.
- Rama comparada: `work`, SHA inicial de la auditoría `7c7d2dad64c6cafb7d1a43da6107075e69fd8c68`.
- Entorno registrado por pytest: Python 3.12.13, pytest 9.0.3.

## Comando exacto y resultado

Se ejecutó, sin opciones adicionales, en ambos árboles:

```console
python -m pytest tests/integration/test_run_repl_equivalence.py -q
```

| árbol | exit code | resumen | registro literal |
|---|---:|---|---|
| `242a5a6a...` | 1 | 1 failed, 41 passed | `pytest_242a5a6_q.log` |
| rama `work` | 1 | 1 failed, 41 passed | `pytest_rama_q.log` |

Los ficheros `.exitcode` conservan el código separado del stream combinado. Los registros `*_casos.log`, obtenidos adicionalmente con `-vv` (sin sustituir las ejecuciones exactas), enumeran los 42 node ids y sus resultados. Las diferencias de tiempos no son diferencias funcionales.

## Comparación caso por caso

Para los casos `PASSED`, «coincide» significa que se cumplieron las salidas, estados y excepciones expresadas por las aserciones del propio caso en ambos árboles; pytest no expone valores intermedios de aserciones exitosas. El único fallo no alcanza las comparaciones posteriores de tipo/mensaje ni genera stdout/stderr: esperaba una excepción del pipeline y la salida real fue ejecución normal (ninguna excepción).

| test (node id) | base | rama | excepción esperada / real | salida esperada / real |
|---|---|---|---|---|
| `test_misma_secuencia_semantica_equivale_entre_run_y_repl` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_mutacion_en_mientras_y_lectura_posterior_persisten_en_repl` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_persistencia_basica_var_x_e_impresion_equivale_entre_run_y_repl` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_bloque_si_comparte_estado_posterior_equivale_entre_run_y_repl` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_repl_evalua_expresiones_con_estado_persistente[x + 10-15]` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_repl_evalua_expresiones_con_estado_persistente[x * 2-10]` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_repl_fallback_expresion_sin_duplicar_salida_y_nameerror_real_preservado` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_repl_no_suprime_error_real_en_expresion_con_variable_no_declarada` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_repl_statement_normal_imprimir_no_duplica_salida` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_instrucciones_posteriores_a_si_y_llamadas_con_valor_se_ejecutan` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_repl_llamada_funcion_auditoria_una_sola_vez_y_retorno_correcto` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_repl_definir_funcion_triple_no_produce_salida_en_definicion` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_repl_incremental_var_var_imprimir_y_nameerror_sin_temporales_internas` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_repl_mantiene_estado_tras_error_intermedio` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_repl_persistencia_entre_entradas_tras_error_intermedio_real` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_anidacion_condicional_bucle_equivale_en_salida_y_estado` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_error_semantico_y_runtime_equivalen_en_tipo_y_mensaje[no_definida = 1]` | FAILED | FAILED | `Exception` / ninguna (en ambos árboles) | sin salida antes de la comparación / sin salida; la aserción falla antes de comparar REPL |
| `test_error_semantico_y_runtime_equivalen_en_tipo_y_mensaje[var x = 10 / 0]` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_error_sintactico_equivale_en_tipo_y_mensaje[imprimir("cadena sin cerrar)]` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_error_sintactico_equivale_en_tipo_y_mensaje[si verdadero imprimir(1)]` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_runtime_estado_final_paridad_run_vs_repl[mutacion_en_mientras_persiste-var contador = 10-mientras verdadero:\n    contador = 15\n    romper\nfin-variables_esperadas0]` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_runtime_estado_final_paridad_run_vs_repl[mutacion_en_mientras_persiste_fuera_del_bucle-var total = 1-mientras verdadero:\n    total = 4\n    romper\nfin-variables_esperadas1]` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_runtime_estado_final_paridad_run_vs_repl[mientras_con_continuar_romper_y_variable_local_visible-var paso = falso-mientras verdadero:\n    si paso:\n        var ultimo = 2\n        romper\n    fin\n    paso = verdadero\n    continuar\nfin-variables_esperadas2]` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_runtime_estado_final_paridad_run_vs_repl[bloque_anidado_shadowing_y_set_dirigido-var raiz = 100-func ajustar():\n    var raiz = 5\n    raiz = 9\n    retorno raiz\nfin\nvar resultado = ajustar()-variables_esperadas3]` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_sandbox_normaliza_safe_mode_y_validadores_igual_en_run_y_repl` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_paridad_funcional_acotada_run_y_repl_en_declaraciones_secuenciales[var-imprimir("antes")\nvar x = 3\nimprimir("despues")-estado_esperado0]` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_paridad_funcional_acotada_run_y_repl_en_declaraciones_secuenciales[variable-imprimir("antes")\nvariable y := 4\nimprimir("despues")-estado_esperado1]` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_run_no_corta_sentencias_posteriores_en_bloque_si` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_run_retorno_fuera_de_funcion_muestra_error_corto_sin_traceback` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_run_conservar_control_break_y_continue_en_mientras` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_run_acepta_utf8_bom_en_frontera_de_entrada[True]` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_run_acepta_utf8_bom_en_frontera_de_entrada[False]` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_run_utf8_bom_y_sin_bom_producen_salida_identica` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_build_rechaza_programa_semanticamente_invalido_sin_generar_codigo` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_build_utf8_bom_y_sin_bom_compilan_sin_token_bom` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_run_usar_modulos_oficiales_produce_salida_exacta` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_run_error_lexico_sigue_siendo_corto_sin_traceback_con_y_sin_bom` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_run_usar_numpy_rechaza_sin_traceback_ni_error_duplicado` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_run_usar_archivo_habilita_existe_readme_local` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_run_usar_archivo_existe_parent_es_falso_por_wrapper_seguro` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_run_existe_sin_usar_archivo_permanece_bloqueado` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |
| `test_run_error_funcion_no_declarada_conserva_identificador_completo` | PASSED | PASSED | contrato del caso / coincide | contrato del caso / coincide |

## Causa concreta del resultado idéntico

El parámetro que falla es `no_definida = 1`. La prueba lo clasifica como error semántico y exige que `ejecutar_pipeline_explicito` lance una excepción. Sin embargo, la fuente normativa define `IDENTIFICADOR "=" expr` como una asignación válida y usa `x = 10` como ejemplo. El analizador semántico implementa ese contrato declarando el nombre cuando todavía no existe. Por ello el pipeline termina normalmente y `pytest.raises(Exception)` falla con `DID NOT RAISE`; no hay una excepción ni una salida real que comparar con el REPL.

No se modificó la prueba para hacerla pasar: hacerlo cambiaría/debilitaría el contrato solicitado. Tampoco se modificaron Lexer ni Parser.

### Por qué no procede de #3430/#3431

1. El test y su expectativa provienen del commit raíz histórico `994cd4f`, anterior a ambos PR.
2. El fichero de integración no cambia entre `242a5a6a...` y la rama auditada.
3. #3430 se concentra en capacidades y aislamiento de `usar`; #3431 en identidad canónica/imports y sus contratos asociados. Ninguno cambia la regla normativa de que una asignación simple introduce el identificador.
4. La reproducción aislada del node id también falla, por lo que no depende del orden, del lifecycle de otro test ni de contaminación de `sys.modules`. No se añadió ninguna limpieza de `sys.modules` ni alias legacy.

Conclusión: los resultados pedidos son funcionalmente idénticos y el fallo es una expectativa histórica incompatible con la sintaxis normativa, no una regresión de lifecycle/aislamiento atribuible a #3430/#3431.

## Contratos REPL/script tocados por #3431

Se ejecutó en la rama actual:

```console
python -m pytest tests/cli/test_repl_script_parity_contract.py tests/integration/test_repl_usar_entrypoints_contract.py -q
```

Resultado: exit code 1; 109 passed y 5 failed. Los cinco fallos son los parámetros `configuracion`, `ruta`, `serializacion`, `sistema` y `temporal` de `test_repl_contract_pipeline_completo_por_modulo_canonico`; todos reciben `PermissionError` por denegación de `filesystem.read` o `filesystem.write`. El registro completo está en `contratos_3431_rama.log`. Como control diagnóstico, la misma suite en el worktree base dio exit code 0 (114 passed), conservado en `contratos_3431_242a5a6.log`. Esta diferencia es un hallazgo posterior y separado del resultado idéntico de `test_run_repl_equivalence.py`; no se mezcló una remediación adicional en esta auditoría incremental.
