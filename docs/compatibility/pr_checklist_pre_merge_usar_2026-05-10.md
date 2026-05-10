# PR Checklist pre-merge: `usar` (2026-05-10)

## Alcance revisado
- Rango inspeccionado: `a665cd3..HEAD`.
- Archivos modificados en el rango:
  - `src/pcobra/core/interpreter.py`
  - `tests/unit/test_usar.py`

## Criterios de aceptación
- [x] **Sin cambios en lexer/parser críticos**.
  - Verificado que **no** aparecen en el diff:
    - `src/pcobra/core/lexer.py`
    - `src/pcobra/core/parser.py`
    - `src/pcobra/cobra/core/lexer.py`
    - `src/pcobra/cobra/core/parser.py`
- [x] **No se introdujo sintaxis nueva**.
  - El cambio funcional en código agrega solo un helper de logging (`_resumen_conflictos_usar`) y ajuste de mensajes `warning`; no hay edición de gramática, parser ni lexer.
- [x] **No se relajó la sanitización global de `usar`**.
  - Se mantiene el flujo de detección de conflictos de saneamiento; únicamente se compacta la salida de log a `count=<n>` en modo normal.
- [x] **No se permitió import externo directo ni bypass de sandbox**.
  - No hay cambios en rutas permitidas/import policy ni en validaciones de sandbox dentro del rango inspeccionado.
- [x] **Checklist documentado**.
  - Este documento deja trazabilidad explícita de la revisión pre-merge solicitada.
