# Informe técnico: binding runtime de `usar "numero"`

## Resumen del problema
Se verificó que `usar "numero"` resolvía e inyectaba símbolos saneados en runtime, pero al invocar funciones como `es_finito(10)` el intérprete caía en la rama de "Función no implementada" porque `ejecutar_llamada_funcion` solo ejecutaba funciones Cobra representadas como `dict` (`tipo == "funcion"`).

## Causa raíz
En `src/pcobra/core/interpreter.py`, `ejecutar_llamada_funcion` obtenía el símbolo por nombre y descartaba cualquier valor que no tuviera el descriptor interno de función Cobra. Los callables Python provenientes de `usar` (ya saneados e inyectados en contexto) no eran ejecutados.

## Cambio aplicado
1. Se mantuvo intacta la ruta de `usar` y su sanitización.
2. Se añadió un bloque mínimo en `ejecutar_llamada_funcion` para soportar `callable(funcion)`:
   - Evalúa argumentos con `self.evaluar_expresion`.
   - Verifica cada argumento con `self._verificar_valor_contexto`.
   - Ejecuta `funcion(*argumentos_resueltos)`.
   - Verifica el resultado con `self._verificar_valor_contexto`.
   - Retorna el resultado.
3. La lógica existente para funciones Cobra definidas por usuario (`dict` con `tipo == "funcion"`) se mantiene sin cambios semánticos.

## Seguridad y superficie pública
- No se añadió import dinámico.
- No se relajó sanitización de `usar`.
- Solo se ejecutan callables ya presentes en el contexto del intérprete.
- Se preserva el rechazo de módulos externos no canónicos en `usar`.

## Cobertura añadida
Se añadieron pruebas unitarias en `tests/unit/test_usar.py` para validar ejecución runtime de callables importados por `usar`:
- `es_finito` ejecutable desde `ejecutar_llamada_funcion`.
- `es_nan` ejecutable desde `ejecutar_llamada_funcion`.

## Archivos modificados
- `src/pcobra/core/interpreter.py`
- `tests/unit/test_usar.py`
- `informe_tecnico_binding_runtime_usar.md`

---

## Trazabilidad solicitada (flujo `usar` y productor de metadata)

### 1) Punto de entrada Cobra-facing en runtime/interprete
- **Entrada principal**: `Interpretador.ejecutar_usar(self, nodo)` en `src/pcobra/core/interpreter.py`.
- Desde esta función se resuelve el módulo canónico permitido, se sanean exports y se prepara la inyección en el contexto activo.

### 2) Flujo hasta la creación de metadata por símbolo
Secuencia observada:
1. `ejecutar_usar` llama a `sanitizar_exports_publicos(modulo, nombre_modulo)` (vía `pcobra.core.usar_loader`) para obtener `mapa_limpio`.
2. Se itera `simbolos_saneados = list(mapa_limpio.items())`.
3. Para cada `(nombre, simbolo)` se construye metadata con:
   - `build_and_validate_usar_symbol_metadata(module_name=nodo.modulo, symbol_name=nombre, callable_obj=simbolo)`.
4. El resultado se valida de nuevo con:
   - `validate_usar_symbol_metadata(nombre, metadata_simbolo)`.
5. La colección resultante queda en `metadata_por_simbolo` y viaja a:
   - `_detectar_conflictos_usar_en_contexto(..., metadata_por_simbolo=...)`.
   - `_inyectar_simbolos_usar_en_contexto(..., metadata_por_simbolo=...)`.
6. En inyección se vuelve a validar (`validate_usar_symbol_metadata`) antes de registrar en:
   - `self._usar_symbol_metadata[nombre]`.
   - `self._validador.registrar_simbolo_publico_usar(..., metadata=dict(metadata_simbolo))` cuando aplica.

### 3) ¿Hay múltiples productores hoy?
Sí, hay **más de un productor/transformador** en la cadena:
- **Productor primario (canónico)**:
  - `build_usar_symbol_metadata(...)` / `build_and_validate_usar_symbol_metadata(...)` en `src/pcobra/core/usar_symbol_policy.py`.
- **Normalizador/validador estricto**:
  - `_normalizar_metadata_simbolo_usar(...)` y `validate_usar_symbol_metadata(...)` en `src/pcobra/core/usar_symbol_policy.py`.
- **Productor/transportista de candidatos de símbolo**:
  - `sanitizar_exports_publicos(...)` y `sanear_exportables_para_usar(...)` (pipeline de saneamiento de exports antes de metadata).
- **Registro secundario en validador runtime**:
  - `registrar_simbolo_publico_usar` (consume metadata ya validada y la replica en `_metadata_simbolos_usar` del validador).

> Conclusión: la **fábrica canónica de metadata** vive en `usar_symbol_policy.py`, pero el pipeline incluye saneamiento previo y validaciones/replicación posteriores.

### 4) Contrato actual observado (claves, tipos, casos especiales)
Contrato canónico impuesto por `validate_usar_symbol_metadata` + `_normalizar_metadata_simbolo_usar`:
- Claves obligatorias:
  - `origin_kind: str` (debe ser `"usar"`; compat legacy: `kind="usar"` se normaliza).
  - `module: str` (módulo Cobra-facing canónico).
  - `symbol: str` (nombre exportado).
  - `callable: bool`.
  - `public_api: bool`.
  - `sanitized: bool`.
  - `backend_exposed: bool`.
- Claves frecuentes adicionales (derivadas por la fábrica canónica):
  - `origin_module`, `canonical_module` (consistencia con `module`).
  - `exported_name` (consistencia con `symbol`).
  - `is_sanitized_wrapper` (consistencia con `sanitized`).
  - `is_public_export`, `introduced_by`, `symbol_name`.
- Tipos esperados:
  - Contenedor metadata: `dict[str, object]` (fail-closed si no es dict).
  - Banderas lógicas (`callable`, `public_api`, `sanitized`, `backend_exposed`): `bool` estricto.
- Casos especiales observados:
  - `archivo.existe`: en `_inyectar_simbolos_usar_en_contexto` hay traza explícita confirmando wrapper sanitizado cuando `module=="archivo"` y `nombre=="existe"`.
  - Wrappers seguros/sanitizados: el contrato exige coherencia entre `sanitized` e `is_sanitized_wrapper` (si está presente).
  - Si metadata falta o contradice claves canónicas, se rechaza con `ValueError` (fail-closed).

### 5) Marcado de fuente upstream para futura normalización canónica
Se deja marcado explícitamente como **fuente upstream** de metadata por símbolo:
- **`build_and_validate_usar_symbol_metadata(...)` en `src/pcobra/core/usar_symbol_policy.py`**.

Justificación:
- Es el primer punto donde se crea metadata estructurada por símbolo en la ruta runtime de `usar`.
- Ya aplica validación canónica inmediata y permite encadenar normalización estricta sin romper invariantes de seguridad.
