# 14. Plan de validación de sintaxis Cobra (parser/lexer/CLI)

## Objetivo
Definir tareas ejecutables para estabilizar la sintaxis de Cobra, garantizando:

1. Parseo correcto de expresiones y bloques.
2. Compatibilidad de imports entre `cobra.*` y `pcobra.*`.
3. Salidas válidas en pruebas unitarias e integración de sintaxis.

## Estado observado (2026-03-31)

### Fallo A: integración de sintaxis no colecciona tests
- Comando: `python -m pytest -q tests/integration/test_transpilador_syntax.py`
- Error: `ImportError: cannot import name 'reverse' from 'cobra.transpilers'`
- Archivo implicado por traceback:
  - `src/pcobra/cobra/cli/commands/transpilar_inverso_cmd.py`
  - `src/pcobra/cobra/transpilers/__init__.py`

### Fallo B: parser base rompe en casos de unidad
- Comando: `PYTHONPATH=src python -m pytest -q tests/unit/test_parser.py tests/unit/test_lexer.py`
- Errores principales:
  - `Token inesperado en declaracion_holobit: TipoToken.RESTA`
  - AST esperado `NodoCondicional`, recibido `NodoAsignacion`

## Backlog de implementación (tareas separadas)

### Tarea 1 — Corregir contrato de imports en transpilado inverso
**Objetivo:** Eliminar la incompatibilidad entre namespaces (`cobra` vs `pcobra`) que bloquea la colección de tests de sintaxis.

**Subtareas:**
1. Revisar exports de `src/pcobra/cobra/transpilers/__init__.py` para exponer explícitamente `reverse`.
2. Unificar en `transpilar_inverso_cmd.py` el import al namespace canónico del proyecto.
3. Añadir test de regresión de import para `reverse` desde CLI.

**Criterio de aceptación:**
- `python -m pytest -q tests/integration/test_transpilador_syntax.py` deja de fallar en colección por `ImportError`.

### Tarea 2 — Arreglar precedencia y dispatch de expresiones en parser
**Objetivo:** Evitar que tokens de operaciones aritméticas caigan en rutas de `declaracion_holobit` cuando no corresponde.

**Subtareas:**
1. Auditar el flujo `expresion -> exp_unario -> termino -> declaracion_holobit` en `parser.py`.
2. Ajustar guardas para que `RESTA` unaria y binaria se enruten a la rama semántica correcta.
3. Añadir pruebas unitarias mínimas para:
   - asignación con resta (`var x = 10 - 2`),
   - negación unaria,
   - mezcla con condicionales.

**Criterio de aceptación:**
- `tests/unit/test_parser.py` pasa en los casos actualmente rotos sin regresiones de lexer.

### Tarea 3 — Corregir construcción de AST en bloques condicionales
**Objetivo:** Asegurar que una secuencia con `si/sino/fin` construye `NodoCondicional` y no se degrada a `NodoAsignacion` en la raíz.

**Subtareas:**
1. Verificar delimitación de bloque y consumo de tokens de control.
2. Revisar orden de parseo de declaraciones previas y el cierre de `fin`.
3. Añadir snapshot textual del AST para caso con asignación + condicional.

**Criterio de aceptación:**
- El test de `NodoCondicional` en parser refleja el nodo raíz esperado.

### Tarea 4 — Matriz de validación sintáctica automatizada
**Objetivo:** Ejecutar una suite corta y fiable para validar sintaxis antes de merge.

**Subtareas:**
1. Crear target (Makefile o script CI) con:
   - `tests/unit/test_lexer.py`
   - `tests/unit/test_parser.py`
   - `tests/integration/test_transpilador_syntax.py`
2. Publicar salida resumida de errores por categoría (import, lexer, parser).
3. Integrar como check recomendado en contribuciones de gramática.

**Criterio de aceptación:**
- Existe un comando único para validar sintaxis y detectar de forma temprana fallos de parsing/import.

## Orden recomendado de ejecución
1. **Tarea 1** (desbloquea integración).
2. **Tarea 2** (estabiliza expresiones).
3. **Tarea 3** (corrige AST de control de flujo).
4. **Tarea 4** (cierre con automatización).

## Definición de terminado (DoD)
- Todas las pruebas de la matriz sintáctica en verde.
- Sin errores de import en colección de tests.
- Sin regresiones en casos base de lexer/parser.
- Documentación de troubleshooting actualizada con errores típicos y solución.
