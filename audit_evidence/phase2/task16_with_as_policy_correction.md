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

Task 16 elimina exclusivamente las dos reglas inglesas del lexer, las dos
expectativas asociadas y la prueba de equivalencia introducida por Task 15. No
elimina la funcionalidad de context manager: `con recurso como r` continúa
siendo la forma funcional soportada.

El estado final esperado es:

```text
con  -> TipoToken.CON
como -> TipoToken.COMO
with -> TipoToken.IDENTIFICADOR
as   -> TipoToken.IDENTIFICADOR
```

Por tanto, `with recurso as r` ya no activa el contrato de context manager de
Cobra.

## 5. Parser y enum

No se modifica el parser porque ya consume los tokens canónicos
`TipoToken.CON` y `TipoToken.COMO`; la corrección pertenece únicamente a la
clasificación léxica de las palabras inglesas. Tampoco se modifica el enum
`TipoToken`: no hacen falta, ni deben crearse, `TipoToken.WITH` o
`TipoToken.AS`.

## 6. Pendiente documental

La presente tarea corrige el registro normativo de Task 14 y documenta el
rollback de Task 15. Cualquier reconciliación futura de otras superficies
documentales históricas queda fuera del alcance de Task 16 y deberá abordarse
de forma independiente.
