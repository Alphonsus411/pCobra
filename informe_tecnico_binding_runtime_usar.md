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
