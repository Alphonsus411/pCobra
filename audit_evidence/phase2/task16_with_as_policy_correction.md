# Phase 2 — Task 16: corrección de política de `with/as`

Fecha de corrección: 2026-09-16.

## 1. Base y alcance

| Dato | Valor |
|---|---|
| SHA base de Task 16 | `423b8c95e4ded87e0b6f404e9c3d43f2759c525e` |
| Estado inicial | limpio; `git status --short` no produjo salida |
| Alcance | rollback funcional mínimo de Task 15 y corrección normativa de Task 14 |

## 2. Interpretación corregida

Task 14 interpretó erróneamente que el mantenedor quería restaurar `with/as`
como aliases funcionales de `con/como`. La decisión real es conservar la
funcionalidad equivalente a los context managers de Python exclusivamente con
la sintaxis española `con/como`.

La clasificación definitiva es **POLÍTICA C — CONSOLIDAR SINTAXIS ESPAÑOLA**:

- **FORMA CANÓNICA Y FUNCIONAL: con/como**
- **WITH/AS: NO SOPORTADOS COMO SINTAXIS COBRA**
- **FUNCIONALIDAD EQUIVALENTE A PYTHON WITH/AS: SÍ, MEDIANTE con/como**

## 3. Regresión introducida por Task 15

Task 15 materializó la interpretación incorrecta añadiendo al lexer core dos
reglas que normalizaban `with` a `TipoToken.CON` y `as` a `TipoToken.COMO`.
También añadió al contrato del lexer esas dos expectativas y una prueba de
equivalencia semántica entre las formas española e inglesa.

## 4. Corrección aplicada

Task 16 elimina exclusivamente las dos reglas inglesas del lexer y las dos
expectativas positivas asociadas. La prueba de equivalencia introducida por
Task 15 se sustituye por cobertura negativa que exige que `with` y `as` sean
identificadores y que `with recurso as r` no se pueda interpretar como un
context manager. No se elimina la funcionalidad de context manager: `con
recurso como r` continúa siendo la forma funcional soportada.

El estado final esperado es:

```text
con  -> TipoToken.CON
como -> TipoToken.COMO
with -> TipoToken.IDENTIFICADOR
as   -> TipoToken.IDENTIFICADOR
```

Por tanto, `with recurso as r` ya no activa el contrato de context manager de
Cobra.

## 5. Bloqueo detectado en el parser

La corrección léxica deja al descubierto una advertencia obsoleta en
`ClassicParser.declaracion_con`: la forma canónica `con recurso como r` entra
en la condición de «mezcla de alias» y recomienda `with ... as`, aunque esa
sintaxis inglesa ya no es válida. Por tanto, no se considera cerrado el ajuste
del parser.

Corregir esa condición exige modificar `src/pcobra/cobra/core/parser.py`. Las
reglas obligatorias de este repositorio prohíben modificar Lexer o Parser sin
autorización explícita y específica; la solicitud de revisión permite
documentar este bloqueo, pero no concede esa autorización. Se detiene aquí ese
hallazgo hasta recibirla. Tampoco se modifica el enum `TipoToken`: no hacen
falta, ni deben crearse, `TipoToken.WITH` o `TipoToken.AS`.

## 6. Pendiente documental

La presente tarea corrige el registro normativo de Task 14 y documenta el
rollback de Task 15. Queda pendiente, y explícitamente bloqueada por la regla
anterior, la eliminación de la advertencia falsa del parser. Cualquier
reconciliación futura de otras superficies documentales históricas queda fuera
del alcance de Task 16 y deberá abordarse de forma independiente.
