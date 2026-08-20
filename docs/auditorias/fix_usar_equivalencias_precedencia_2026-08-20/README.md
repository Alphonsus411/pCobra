# Corrección de precedencia de equivalencias en `usar` — 2026-08-20

## Objetivo y alcance

Este hallazgo corrige exclusivamente la clasificación de cinco nombres que ya
estaban rechazados por la política de saneamiento de símbolos de `usar`. No se
habilita ningún nombre, no se cambia la sintaxis Cobra y no se modifica Lexer ni
Parser. Los demás fallos del triage permanecen fuera de alcance.

## Causa raíz

`append`, `expect`, `filter`, `map` y `unwrap` pertenecían simultáneamente a
`NOMBRES_BLOQUEADOS_USAR` y a
`EQUIVALENCIAS_PROHIBIDAS_A_CANONICAS`. La rama de nombres bloqueados se
evaluaba antes que la clasificación por equivalencia y terminaba el saneamiento
con `explicit_forbidden_name`. Por ello nunca se alcanzaba la información más
específica que el propio mapa ya declaraba: el rechazo con código
`cobra_public_equivalent` y la recomendación del nombre Cobra canónico.

### Precedencia anterior

1. Se consultaba `NOMBRES_BLOQUEADOS_USAR`.
2. Una coincidencia se rechazaba inmediatamente como
   `explicit_forbidden_name`.
3. La pertenencia posterior a `EQUIVALENCIAS_PROHIBIDAS_A_CANONICAS` no podía
   influir en el resultado de esos cinco nombres.

### Precedencia nueva

Al procesar un nombre bloqueado, la política comprueba si también existe en
`EQUIVALENCIAS_PROHIBIDAS_A_CANONICAS`. En ese caso mantiene el rechazo, pero
lo clasifica como `cobra_public_equivalent`; sólo un bloqueo que carezca de
equivalencia conserva `explicit_forbidden_name`. Así, la equivalencia más
específica prevalece sobre el bloqueo genérico sin relajar la política.

| Símbolo rechazado | Equivalente Cobra comunicado |
|---|---|
| `append` | `agregar` |
| `expect` | `obtener_o_error` |
| `filter` | `filtrar` |
| `map` | `mapear` |
| `unwrap` | `obtener_o_error` |

## Archivos modificados

- `src/pcobra/core/usar_symbol_policy.py`: clasificación específica de los
  nombres bloqueados que cuentan con equivalente Cobra.
- `tests/unit/test_usar_symbol_policy.py`: regresiones parametrizadas para los
  cinco solapamientos y para el bloqueo sin equivalencia.
- `docs/auditorias/fix_usar_equivalencias_precedencia_2026-08-20/README.md`:
  este registro de implementación y verificación.

No se modificaron Lexer, Parser, ejemplos, documentación normativa ni pruebas
de los otros hallazgos.

## Verificación dirigida

La suite unitaria de la política verifica los cinco nombres, tanto en el
resultado individual como en el saneamiento de una colección. Los cinco siguen
con `rechazado is True`, no aparecen entre los símbolos permitidos y ahora
devuelven `cobra_public_equivalent` con su recomendación canónica. La misma
suite confirma que `__self__`, presente en `NOMBRES_BLOQUEADOS_USAR` pero sin
entrada en el mapa de equivalencias, continúa devolviendo
`explicit_forbidden_name`.

```console
$ pytest -q tests/unit/test_usar_symbol_policy.py
31 passed in 0.23s
```

Se intentó además recopilar conjuntamente el contrato público y la política:

```console
$ pytest -q tests/unit/test_usar_symbol_policy.py tests/unit/test_usar_loader_public_api_contract.py
ERROR tests/unit/test_usar_loader_public_api_contract.py
1 error in 1.70s
```

Ese intento aislado no llegó a ejecutar pruebas: durante la recopilación,
`tests/conftest.py` antepuso `src/pcobra` y `from cobra import usar_loader`
resolvió `src/pcobra/cobra/usar_loader.py` como paquete de nivel superior; su
import relativo produjo `ImportError: attempted relative import beyond
top-level package`. No se alteró la configuración para ocultar esta limitación.
La suite ampliada, en su orden contractual registrado, sí recopila y ejecuta el
mismo archivo.

## Comparación de la suite ampliada

El baseline documentado antes de la corrección era:

```text
15 failed, 506 passed, 5 skipped
```

Se volvió a ejecutar literalmente la selección de 26 archivos registrada en
`docs/auditoria_holobit_contract_fix.md`:

```console
$ pytest -q tests/integration/test_holobit_tiers.py tests/integration/transpilers/test_holobit_hooks_golden.py tests/unit/test_corelibs_holobit_adapter.py tests/unit/test_holobit_backend_contract_matrix.py tests/unit/test_holobit_corelib_domain_errors.py tests/unit/test_holobit_generation.py tests/unit/test_holobit_graficar_contract.py tests/unit/test_holobit_no_fuga_exports.py tests/unit/test_holobit_runtime_backends.py tests/unit/test_holobit_sdk_compatibility_report.py tests/unit/test_holobit_sdk_fallback_contract.py tests/unit/test_holobit_sdk_integration.py tests/unit/test_holobit_transformacion_extra.py tests/unit/test_parser_holobit.py tests/unit/test_to_js_holobit_runtime_snapshot.py tests/integration/test_repl_usar_entrypoints_contract.py tests/integration/test_usar_canonical_surface_contract.py tests/integration/test_usar_core_contract_full.py tests/integration/test_usar_export_sanitation.py tests/integration/test_usar_public_contract_regression.py tests/integration/test_usar_runtime_contract.py tests/unit/test_usar_loader_public_api_contract.py tests/unit/test_usar_loader_validation.py tests/unit/test_usar_numpy_error_contract.py tests/unit/test_usar_policy_contract.py tests/unit/test_usar_public_contract.py
10 failed, 511 passed, 5 skipped, 2 warnings in 20.34s
```

Desaparecieron **exactamente los cinco fallos del grupo C**, los parámetros
`append`, `expect`, `filter`, `map` y `unwrap` de
`test_politica_de_simbolos_prohibidos_devuelve_codigo_y_mensaje`. Los aprobados
aumentaron de 506 a 511 y los fallidos bajaron de 15 a 10; omitidos y warnings
se mantuvieron. La comparación nominal del resumen de fallos confirma que no
cambió ningún otro nodo. Por tanto, no se activa la condición de detener la
entrega para diagnosticar cambios ajenos al grupo C.

## Fallos históricos restantes (sin corrección en este hallazgo)

Se conservan exactamente los casos 1–6 y 12–15 enumerados en
`docs/auditorias/triage_15_fallos_holobit_usar_2026-08-20/README.md`:

1. La fachada `pcobra.core.holobits` exporta nombres adicionales a la API
   canónica.
2. La misma fachada permite acceder a la clase interna `Holobit`.
3. El contrato legacy consulta backends retirados en
   `BACKEND_FEATURE_GAPS` y encuentra `KeyError: 'wasm'`.
4. Una prueba interpreta una capacidad base `full` de Rust como paridad SDK
   completa.
5. `graficar` puede resolver al submódulo homónimo en vez de a la función en el
   orden de suite.
6. Otra prueba de integración identifica erróneamente a Rust como backend con
   SDK completo al mezclar features generales y Holobit.
12. La fixture espera extensión `.co`, mientras el resolver busca `.cobra`.
13. La fixture de traversal por symlink también usa `.co` y no alcanza el
    control de seguridad de la candidata `.cobra`.
14. El error de módulo inexistente no contiene el diagnóstico público
    estructurado esperado.
15. Una ruta backend no canónica propaga `ValueError` antes de normalizarse en
    la frontera pública.

No se propone ni se incorpora aquí ninguna corrección para esos diez casos.

## Riesgos pendientes

- Permanecen los diez fallos históricos anteriores; pertenecen a superficies
  legacy, matriz de backends, resolución de módulos y traducción de errores.
- `NOMBRES_BLOQUEADOS_USAR` y el mapa de equivalencias siguen siendo catálogos
  independientes: futuras incorporaciones solapadas deben conservar la prueba
  parametrizada para evitar otra divergencia de clasificación.
- La recopilación aislada de ciertos archivos que importan `cobra` continúa
  siendo sensible al orden de `sys.path`; este hallazgo no modifica el entorno
  de pruebas porque sería un problema distinto.
- La corrección cambia el código diagnóstico observado por consumidores para
  esos cinco rechazos, aunque preserva la decisión de seguridad y el mensaje
  con alternativa pública.
