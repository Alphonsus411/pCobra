# Auditoría de valores finitos en el contrato público de Holobit

## Problema encontrado

La frontera pública de Holobit aceptaba `NaN`, `Infinity` y `-Infinity` porque
`_normalizar_valores` comprobaba que cada elemento fuera numérico, pero lo
incorporaba a la salida inmediatamente después de convertirlo a `float`. Estos
valores podían entrar mediante `crear_holobit` o un payload JSON y propagarse a
serialización, proyección, transformación, combinación y medición.

## Solución aplicada

Después de conservar la validación `_es_numero(item)`, cada elemento se
convierte exactamente una vez con `valor_normalizado = float(item)`. Antes de
añadirlo a `salida`, `_normalizar_valores` ejecuta exactamente
`math.isfinite(valor_normalizado)`. Si el resultado es falso, lanza `ValueError`
con el mensaje público de dominio `Todos los valores del holobit deben ser
finitos`.

El rechazo mediante `TypeError` de booleanos, texto, bytes y elementos no
numéricos permanece intacto. Los enteros y `float` finitos continúan
normalizándose a `float`. La validación centralizada protege también las rutas
de deserialización, validación, serialización, proyección, transformación,
combinación y medición sin duplicar lógica productiva.

## Archivos modificados

- `src/pcobra/corelibs/holobit.py`: comprobación de finitud en
  `_normalizar_valores`.
- `tests/unit/test_corelibs_holobit_adapter.py`: casos parametrizados de valores
  no finitos, payloads JSON, validación booleana, operaciones protegidas y
  roundtrip positivo con enteros, cero, negativos y floats finitos.
- `docs/auditoria_holobit_contract_fix.md`: este informe de auditoría.

## Verificaciones ejecutadas

Los comandos se ejecutaron desde la raíz del repositorio, en el orden
solicitado:

1. Pruebas dirigidas del nuevo contrato:

   ```console
   $ pytest -q tests/unit/test_corelibs_holobit_adapter.py -k 'no_finitos or valores_no_finitos or public_contract_roundtrip'
   15 passed, 17 deselected in 2.02s
   ```

2. Archivo unitario completo del adaptador Holobit:

   ```console
   $ pytest -q tests/unit/test_corelibs_holobit_adapter.py
   32 passed in 1.67s
   ```

3. Suite ampliada documentada:

   ```console
   $ pytest -q tests/integration/test_holobit_tiers.py tests/integration/transpilers/test_holobit_hooks_golden.py tests/unit/test_corelibs_holobit_adapter.py tests/unit/test_holobit_backend_contract_matrix.py tests/unit/test_holobit_corelib_domain_errors.py tests/unit/test_holobit_generation.py tests/unit/test_holobit_graficar_contract.py tests/unit/test_holobit_no_fuga_exports.py tests/unit/test_holobit_runtime_backends.py tests/unit/test_holobit_sdk_compatibility_report.py tests/unit/test_holobit_sdk_fallback_contract.py tests/unit/test_holobit_sdk_integration.py tests/unit/test_holobit_transformacion_extra.py tests/unit/test_parser_holobit.py tests/unit/test_to_js_holobit_runtime_snapshot.py tests/integration/test_repl_usar_entrypoints_contract.py tests/integration/test_usar_canonical_surface_contract.py tests/integration/test_usar_core_contract_full.py tests/integration/test_usar_export_sanitation.py tests/integration/test_usar_public_contract_regression.py tests/integration/test_usar_runtime_contract.py tests/unit/test_usar_loader_public_api_contract.py tests/unit/test_usar_loader_validation.py tests/unit/test_usar_numpy_error_contract.py tests/unit/test_usar_policy_contract.py tests/unit/test_usar_public_contract.py
   15 failed, 506 passed, 5 skipped, 2 warnings in 12.46s
   ```

   El resultado conserva **exactamente el baseline de 15 fallos históricos**.
   Los fallos siguen perteneciendo a exportaciones históricas de
   `pcobra.core.holobits`, la matriz de compatibilidad de backends y contratos
   generales de `usar`; ninguno corresponde a la nueva validación de finitud.
   No se modificaron sus pruebas ni los subsistemas afectados para ocultarlos.

## Riesgos pendientes

- Los 15 fallos históricos de la suite ampliada permanecen pendientes y fuera
  del alcance incremental de este hallazgo.
- La protección depende de que toda estructura pública continúe atravesando
  `_normalizar_valores`; las operaciones públicas actuales sí comparten esa
  frontera y quedan cubiertas por las pruebas.
- Una indisponibilidad o un fallo del runtime interno todavía puede impedir una
  operación; este cambio no modifica la traducción existente de esos errores.

## Confirmación de alcance

El cambio no modifica lexer, parser, AST, transpiladores, adaptadores de
imports, `PUBLIC_API_HOLOBIT`, `__all__` ni el contrato de `graficar`.
