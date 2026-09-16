# Phase 2 — Task 14: decisión del mantenedor sobre `with/as`

Fecha de registro: 2026-09-16.

## 1. SHA auditado y alcance

| Dato | Valor |
|---|---|
| SHA auditado | `853c6fcffe77409ccf5ea203b0963c335cc9a3ef` |
| Naturaleza | decisión normativa exclusivamente documental |
| Implementación funcional | fuera de alcance; pendiente de Task 15 |

Task 14 registra el contrato decidido por el mantenedor. No restaura aliases,
no modifica el lenguaje ejecutable y no anticipa cambios de implementación.

## 2. Antecedentes

Esta decisión resuelve la cuestión normativa documentada por los siguientes
antecedentes:

- **Task 11B**, que reconstruyó el origen y el carácter oficial del soporte;
- **Task 12**, que corrigió el resaltado sin restaurar la ejecución;
- **Task 13**, que concluyó `POLÍTICA D — EVIDENCIA INSUFICIENTE` ante la
  ausencia de una decisión normativa inequívoca;
- la PR histórica **#725**;
- el commit histórico `48ae0e06366466a67a7d004333a449c20e768521`,
  que introdujo soporte oficial de `with/as` como aliases de `con/como`;
- el refactor `193c2d792ec1144f89b5ecdb878178f2b3af6402`, que retiró
  funcionalmente ese soporte sin una deprecación formal y dejó superficies
  contradictorias.

La presente decisión aporta la autoridad normativa que faltaba en Task 13; no
reinterpreta la divergencia existente como una implementación ya terminada.

## 3. Decisión del mantenedor

Se adopta inequívocamente **POLÍTICA A — RESTAURAR COMPATIBILIDAD COMPLETA**:

- `con` es la palabra canónica en español equivalente a Python `with`;
- `como` es la palabra canónica en español equivalente a Python `as`;
- `with` debe aceptarse como alias funcional soportado de `con`;
- `as` debe aceptarse como alias funcional soportado de `como`;
- los ejemplos principales y la documentación principal deben seguir
  priorizando la sintaxis española `con/como`.

Los aliases ingleses son parte de la compatibilidad admitida, pero no desplazan
ni igualan la prioridad documental de la forma canónica española.

## 4. Motivación

La decisión se basa conjuntamente en:

1. la compatibilidad con programas históricos;
2. el soporte oficial previo de `with/as`;
3. la familiaridad de estas formas para usuarios procedentes de Python;
4. la política ya existente de aliases bilingües en otras construcciones de
   pCobra;
5. el deseo de evitar una ruptura innecesaria de programas anteriormente
   válidos.

## 5. Arquitectura preferida para la implementación futura

Task 15 debe intentar una normalización léxica hacia los tokens canónicos
españoles:

```text
con  -> TipoToken.CON
with -> TipoToken.CON

como -> TipoToken.COMO
as   -> TipoToken.COMO
```

En particular, la normalización relevante para los aliases es:

```text
with -> CON
as   -> COMO
```

El parser debe continuar trabajando conceptualmente con `TipoToken.CON` y
`TipoToken.COMO`. No deben recrearse tokens ingleses independientes
`TipoToken.WITH` y `TipoToken.AS`, salvo que Task 15 demuestre un impedimento
técnico imprescindible.

Esto es una **decisión arquitectónica preferida para una implementación
futura**, no una afirmación de que Task 14 la haya implementado.

## 6. Compatibilidad esperada

La política objetivo debe permitir la forma canónica:

```cobra
con recurso como r:
    ...
fin
```

y el alias compatible:

```cobra
with recurso as r:
    ...
fin
```

Ambas formas deben ser funcionalmente equivalentes. La primera es la forma
canónica y recomendada; la segunda es un alias funcional soportado.

## 7. Fuera de alcance de Task 14

Task 14 no decide ni implementa todavía:

- cambios concretos del lexer;
- tests exactos;
- cambios del parser;
- modificaciones de EBNF;
- actualizaciones de documentación pública;
- estrategia de release.

Estas materias pertenecen a Task 15 o a tareas posteriores. En particular,
Task 14 no restaura aliases funcionales, no añade tokens y no modifica Lexer ni
Parser.

## 8. Contrato mínimo y criterios de aceptación para Task 15

Una implementación futura deberá verificar, como mínimo:

1. `Lexer("con")` produce `TipoToken.CON`.
2. `Lexer("with")` produce `TipoToken.CON`.
3. `Lexer("como")` produce `TipoToken.COMO`.
4. `Lexer("as")` produce `TipoToken.COMO`.
5. `con recurso como r` sigue funcionando.
6. `with recurso as r` vuelve a funcionar.
7. Ambas formas producen una representación semántica equivalente.
8. No se requieren `TipoToken.WITH` ni `TipoToken.AS`, salvo impedimento
   técnico demostrado.
9. No se rompe la sintaxis española existente.
10. REPL y core deben quedar coherentes.

Estos puntos constituyen el contrato de la tarea futura; ninguno queda
implementado por este documento.

## 9. Clasificación final

**POLÍTICA A — RESTAURAR COMPATIBILIDAD COMPLETA**

**FORMA CANÓNICA: con/como**

**ALIASES SOPORTADOS: with/as**

**IMPLEMENTACIÓN: pendiente de Task 15**
