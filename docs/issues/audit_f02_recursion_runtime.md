# F-02 — recursividad legítima detectada como ciclo

## Clasificación y alcance

- **Prioridad de auditoría:** 2.
- **Severidad:** **P1**. El fallo bloqueaba programas Cobra válidos que usan
  recursividad, pero no comprometía el proceso anfitrión ni producía pérdida de
  datos.
- **Área:** intérprete/runtime.
- **Estado:** corregido y verificado.

Esta unidad de trabajo trata únicamente F-02. No modifica Lexer, Parser,
sintaxis, ejemplos ni interfaces públicas.

## Reproducción desde fuente Cobra

La regresión
`tests/unit/test_interpreter_recursion_runtime.py::test_factorial_recursivo_oficial_ejecuta_sin_falso_ciclo_runtime`
lee `examples/avanzados/funciones/factorial_recursivo.cobra` y lo ejecuta por
`RunService.ejecutar_normal`.

Antes de la reparación, la llamada recursiva reutilizaba objetos expresión del
cuerpo de la función. El seguimiento de evaluación consideraba únicamente la
identidad del objeto y encontraba esa identidad todavía activa en la llamada
exterior. El resultado era el falso positivo `Recursive evaluation detected`
en lugar del factorial calculado.

## Punto más tardío correcto

El AST producido desde la fuente ya representa correctamente la declaración y
la llamada de función. Por ello, el punto correcto de reparación es el
intérprete: la clave temporal de evaluación usa la identidad de expresión junto
con la profundidad de llamada. Cada marco recursivo puede evaluar legítimamente
la misma expresión, sin desactivar la protección dentro de un mismo marco.

La validación estructural permanece separada y continúa rechazando ciclos
reales del AST por identidad. No se requirió ningún cambio gramatical.

## Regresión y comparación

| Aspecto | Antes | Después |
|---|---|---|
| Programa público | El factorial recursivo terminaba con error de falsa evaluación circular. | Termina con código 0 e imprime `120`. |
| Ciclo estructural real | Debía rechazarse. | Se sigue rechazando antes de ejecutar el AST. |
| Interfaces públicas | Sin cambio requerido. | `RunService.ejecutar_normal` conserva su contrato. |
| Lexer / Parser | No eran el origen. | Permanecen intactos. |

## Archivos y verificaciones

- Producción responsable: `src/pcobra/core/interpreter.py`.
- Regresión desde fuente: `tests/unit/test_interpreter_recursion_runtime.py`.
- Suite relacionada: `tests/unit/test_interpreter_cycles.py`.
- Trazabilidad consolidada: secciones 10 y 11 de
  `INFORME_AUDITORIA_PCOBRA_2026-07-15.md`.
