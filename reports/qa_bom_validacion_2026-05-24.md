# Validación BOM UTF-8 (2026-05-24)

## Objetivo
Verificar que el runtime/CLI mantiene el comportamiento previo de aceptación de archivos con BOM UTF-8 en frontera de entrada.

## Pruebas identificadas
- `tests/cli/test_run_service_input_normalization.py`
  - `test_normalizar_codigo_entrada_remueve_solo_bom_inicial`
  - `test_normalizar_codigo_entrada_no_toca_bom_no_inicial`
  - `test_normalizar_codigo_entrada_respeta_utf8_sin_bom`
- `tests/integration/test_run_repl_equivalence.py`
  - `test_run_acepta_utf8_bom_en_frontera_de_entrada`
  - `test_run_utf8_bom_y_sin_bom_producen_salida_identica`
  - `test_run_error_lexico_sigue_siendo_corto_sin_traceback_con_y_sin_bom`

## Ejecución
Comando ejecutado:

```bash
pytest -q tests/cli/test_run_service_input_normalization.py tests/integration/test_run_repl_equivalence.py -k bom
```

Resultado:
- 7 tests `passed`
- 33 tests `deselected`
- 1 warning deprecación no bloqueante

## Conclusión
El comportamiento final observado es consistente con el esperado/preexistente:
- Se acepta correctamente entrada con BOM UTF-8 en el borde de ejecución.
- La salida entre archivos con y sin BOM se mantiene equivalente.
- No se detectan regresiones en la normalización de BOM en el punto de entrada.
