# Auditoría de la corrección del contrato público de Holobit

## Problema encontrado

La función pública `graficar` de la corelib declaraba y validaba una salida de
tipo `str`. Esa expectativa era incompatible con el runtime interno: la
operación de graficado se ejecuta por efecto lateral y su retorno normal es
`None`. Como consecuencia, una ejecución interna correcta podía terminar en un
`TypeError` al atravesar la corelib, únicamente porque `None` no satisfacía el
contrato público de texto.

## Solución aplicada

La frontera pública deja de propagar o interpretar el valor devuelto por la
implementación interna. Después de que el adaptador complete la operación sin
excepciones, `graficar` construye y retorna exactamente:

```json
{"estado": "ok"}
```

Antes de entregarlo, el resultado pasa por la validación JSON-safe de la
corelib. El retorno interno se descarta deliberadamente: tanto el `None`
esperado como cualquier otro objeto que pudiera devolver el SDK permanecen
detrás del adaptador y no alteran ni contaminan la respuesta pública.

## Archivos modificados

El cambio mínimo realizado en esta tarea de documentación modifica únicamente:

- `docs/auditoria_holobit_contract_fix.md` (este informe).

No se realizaron cambios adicionales al runtime, a pruebas ni a otros
documentos durante esta tarea.

## Verificaciones ejecutadas

Los comandos se ejecutaron desde la raíz del repositorio, en el orden solicitado:

1. Prueba dirigida del retorno público de `graficar`:

   ```console
   $ pytest -q tests/unit/test_holobit_graficar_contract.py
   3 passed in 2.57s
   ```

   Resultado: **correcto** (código de salida 0). Cubre el retorno fijo JSON-safe,
   el descarte del objeto interno del SDK y el saneamiento de sus excepciones.

2. Suites de Holobit y contratos relacionados de `usar`:

   ```console
   $ pytest -q tests/integration/test_holobit_tiers.py tests/integration/transpilers/test_holobit_hooks_golden.py tests/unit/test_corelibs_holobit_adapter.py tests/unit/test_holobit_backend_contract_matrix.py tests/unit/test_holobit_corelib_domain_errors.py tests/unit/test_holobit_generation.py tests/unit/test_holobit_graficar_contract.py tests/unit/test_holobit_no_fuga_exports.py tests/unit/test_holobit_runtime_backends.py tests/unit/test_holobit_sdk_compatibility_report.py tests/unit/test_holobit_sdk_fallback_contract.py tests/unit/test_holobit_sdk_integration.py tests/unit/test_holobit_transformacion_extra.py tests/unit/test_parser_holobit.py tests/unit/test_to_js_holobit_runtime_snapshot.py tests/integration/test_repl_usar_entrypoints_contract.py tests/integration/test_usar_canonical_surface_contract.py tests/integration/test_usar_core_contract_full.py tests/integration/test_usar_export_sanitation.py tests/integration/test_usar_public_contract_regression.py tests/integration/test_usar_runtime_contract.py tests/unit/test_usar_loader_public_api_contract.py tests/unit/test_usar_loader_validation.py tests/unit/test_usar_numpy_error_contract.py tests/unit/test_usar_policy_contract.py tests/unit/test_usar_public_contract.py
   15 failed, 492 passed, 5 skipped, 2 warnings in 14.22s
   ```

   Resultado: **con fallos preexistentes fuera del hallazgo dirigido** (código de
   salida 1). Los 15 fallos corresponden a contratos históricos inconsistentes
   en exportaciones de `pcobra.core.holobits`, la matriz de compatibilidad de
   backends y validaciones generales de `usar`. No se modificaron runtime,
   pruebas, lexer, parser, AST ni transpiladores para ocultarlos o mezclarlos con
   la estabilización ya implementada de `graficar`.

3. Comprobaciones del parche final:

   - `git diff --check`: sin errores.
   - `git diff --name-only`: únicamente
     `docs/auditoria_holobit_contract_fix.md`; no aparecen rutas de lexer,
     parser, AST ni transpiladores.
   - Revisión de `git diff`: no amplía `PUBLIC_API_HOLOBIT` ni `__all__`.

## Riesgos pendientes

- La proyección y las operaciones completas de Holobit en el runtime Python
  siguen dependiendo de `holobit_sdk`.
- Los objetos, las excepciones y los módulos de `holobit_sdk` permanecen detrás
  del adaptador interno: no forman parte del retorno público de `graficar` ni se
  exponen a través de él.
- Una indisponibilidad o un fallo del SDK todavía puede impedir la operación;
  la frontera pública debe continuar traduciendo ese fallo sin filtrar detalles
  internos.

## Confirmación de alcance

Se confirma expresamente que en esta tarea **no fueron modificados** el lexer,
el parser, el AST, los transpiladores, `PUBLIC_API_HOLOBIT` ni `__all__`.
