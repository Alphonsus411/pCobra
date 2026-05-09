# Informe QA: `usar "numero"` y binding runtime de callables

## 1) Contexto del bug reportado en REPL

Se reportó una regresión en REPL donde, tras ejecutar `usar "numero"`, llamadas como `es_finito(10)` o `es_nan(10)` podían terminar en el mensaje _"Función '...' no implementada"_ en lugar de ejecutarse como callables Python inyectados por `usar`.

Contexto funcional esperado en pCobra:

- La sintaxis de compatibilidad `usar "numero"` debe resolverse con semántica plana de Cobra (`usar numero`), inyectando símbolos públicos al contexto activo.
- Las funciones públicas de `numero` (p.ej. `es_finito`, `es_nan`) deben quedar invocables como funciones globales en REPL, sin prefijo de namespace.
- En runtime, `ejecutar_llamada_funcion` debe enrutar esos símbolos por la rama `callable(funcion)`.

## 2) Evidencia de implementación actual en `src/pcobra/core/interpreter.py`

### 2.1 `ejecutar_llamada_funcion` (rama `callable(funcion)`)

Evidencia observada:

- En `ejecutar_llamada_funcion`, cuando la resolución de nombre retorna un objeto callable, se ejecuta la rama `if callable(funcion):`.
- En esa rama se evalúan y validan argumentos (`self.evaluar_expresion`, `self._verificar_valor_contexto`) y luego se invoca directamente `resultado = funcion(*argumentos_resueltos)`.
- El resultado también se valida antes de retornarse.
- Esta ruta evita caer en la rama de funciones de usuario tipo dict y, por lo tanto, evita el mensaje de _no implementada_ para callables válidos cargados por `usar`.

Conclusión: el runtime actual sí contempla explícitamente callables Python inyectados en contexto.

### 2.2 `ejecutar_usar`

Evidencia observada:

- `ejecutar_usar` documenta explícitamente la compatibilidad obligatoria: se acepta `usar "numero"`, pero se normaliza a la semántica oficial plana.
- El resolver interno (`_resolver_carga_modulo_usar`) restringe la carga al catálogo canónico Cobra, validando allowlist, módulos públicos y bandera _Cobra-facing_.
- Tras cargar módulo oficial, aplica saneamiento de exportables con `sanitizar_exports_publicos`.
- Realiza preflight de colisiones mediante `_detectar_conflictos_usar_en_contexto` y, si hay conflictos, aborta atómicamente según política.
- Si no hay conflictos, inyecta símbolos saneados con `_inyectar_simbolos_usar_en_contexto`.

Conclusión: `usar` sí realiza el binding de funciones públicas al contexto de ejecución de manera controlada y atómica.

### 2.3 Helper `_inyectar_simbolos_usar_en_contexto`

Evidencia observada:

- El helper centraliza el binding al entorno activo (`contexto_actual = self.contextos[-1]`).
- Define cada símbolo con `contexto_actual.define(nombre, simbolo)`.
- Revalida colisión en runtime (`runtime_recheck`) para impedir sobrescrituras silenciosas si no está habilitada `permitir_sobrescritura`.
- Ante colisión runtime lanza `NameError` estructurado con código `usar_error[conflicto_simbolo]`.

Conclusión: el binding queda encapsulado en un único punto con protección de colisiones.

## 3) Confirmación de no cambios requeridos en lexer/parser

Por inspección del contrato actual:

- La compatibilidad de sintaxis `usar "numero"` ya está asumida y documentada en `ejecutar_usar`.
- El comportamiento reportado (invocación de callables ya inyectados) es de runtime del intérprete, no de tokenización ni parseo.
- Los tests de contrato REPL ejercitan explícitamente esa sintaxis de compatibilidad y la semántica plana, reforzando que lexer/parser no son el punto de ajuste para este caso.

Conclusión: no se observan cambios requeridos en lexer/parser para este bug específico.

## 4) Riesgos residuales y criterios de aceptación validados por inspección

### Riesgos residuales

- **Colisiones de símbolos**: si el usuario ya definió nombres como `es_finito`, `usar` falla por diseño (atómico), lo que puede percibirse como bloqueo funcional si no se usa alias.
- **Política de exportación**: cambios futuros en `__all__`/saneamiento podrían ocultar símbolos esperados sin romper carga del módulo, generando fallos de disponibilidad de funciones concretas.
- **Divergencia REPL vs otros entrypoints**: aunque el flujo está unificado, cambios de wiring en entrypoints podrían reintroducir diferencias de comportamiento observable.

### Criterios de aceptación (inspección)

- `usar "numero"` inyecta `es_finito` y/o `es_nan` en el contexto activo.
- `ejecutar_llamada_funcion("es_finito", [10])` toma la rama `callable(funcion)` y retorna booleano válido.
- No aparece el mensaje _"Función 'es_finito' no implementada"_ cuando el símbolo existe e implementa callable.
- Si hay colisión previa de símbolo, la inyección falla de forma atómica y explícita (sin sobrescribir).
- Intentos de módulo fuera de catálogo (`numpy`, `requests`, etc.) fallan por política de seguridad de `usar`.

## 5) Tests relevantes existentes (`tests/unit/test_usar.py` e integración)

### Unit (`tests/unit/test_usar.py`)

- `test_repl_usar_numero_inyecta_funciones_globales`
- `test_repl_usar_numero_permite_es_finito_sin_prefijo`
- `test_repl_usar_numero_ejecuta_callable_runtime_es_finito`
- `test_repl_usar_numero_ejecuta_callable_runtime_es_nan`
- `test_repl_usar_texto_inyecta_funciones_globales`
- `test_repl_usar_texto_permite_a_snake_sin_prefijo`

### Integración (selección directamente relacionada al bug/contrato)

- `tests/integration/test_repl_entrypoint_numero_callable_output.py`
  - `test_entrypoint_repl_real_numero_callable_y_stdout_canonico_sin_error_no_implementada`
  - `test_entrypoint_repl_numero_callable_output_regresion_binding_runtime`
  - `test_entrypoint_repl_real_numero_callable_directo_sin_no_implementada`
- `tests/integration/test_repl_usar_entrypoints_contract.py`
  - `test_repl_contract_sintaxis_usar_compat_parser_semantica_plana_numero_sin_prefijo`
  - `test_repl_contract_sintaxis_usar_compat_parser_semantica_plana_numpy_restringido_atomico`
  - `test_repl_contract_sintaxis_usar_compat_parser_semantica_plana_colision_no_sobrescribe_usuario`
- `tests/integration/test_usar_core_contract_full.py`
  - `test_01_numero_exporta_solo_espanol`
- `tests/integration/test_usar_canonical_surface_contract.py`
  - `test_caso_1_numero_superficie_publica_espanol`
- `tests/integration/test_usar_runtime_contract.py`
  - Casos de contrato runtime de `usar` y restricciones REPL (incluye rechazo de módulos fuera de allowlist).

