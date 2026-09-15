# Phase 2 — Task 7: forense de TipoToken.TRY

## 1. SHA auditado

La revisión retrospectiva se realizó sobre `0e8d59d618e6072f3b99de2231a718f1e4bd4a0f`, que era el `HEAD` exacto de la rama local `work` al comenzar la auditoría. Ese commit es el merge de la PR #3582 y tiene como padres la base y el head de la reparación:

- base: `0f49b7367b80877e395677e85c9a61813664b4d4`;
- head: `c7dfd193055d8d01421048448bbc34f9c0e88a23`;
- merge: `0e8d59d618e6072f3b99de2231a718f1e4bd4a0f`.

Los comandos iniciales `git status --short`, `git rev-parse HEAD`, `git branch --show-current` y `git log --oneline -10` confirmaron respectivamente un árbol limpio, el SHA anterior, la rama `work` y que el merge de #3582 era el commit más reciente.

## 2. Entorno

- Fecha de la comprobación: 2026-09-15 (UTC).
- Sistema: Linux `6.18.44`, arquitectura `x86_64`.
- Python: `3.12.13`.
- pytest: `9.0.3`.
- Repositorio local: `/workspace/pCobra`.

La evidencia histórica se obtuvo con `git show` y `git diff` directamente de los objetos locales, sin alterar el checkout. El estado de Actions se consultó en la API pública de GitHub para el SHA head de #3582 y, como comprobación adicional, para su merge.

## 3. Estado del enum

`TipoToken` está definido en `src/pcobra/cobra/core/lexer.py`. En el SHA auditado el enum contiene exactamente los miembros canónicos relevantes:

- `TipoToken.INTENTAR` (`"INTENTAR"`);
- `TipoToken.CAPTURAR` (`"CAPTURAR"`);
- `TipoToken.LANZAR` (`"LANZAR"`).

No contiene miembros llamados `TRY`, `CATCH` ni `THROW`. Se verificó tanto por inspección de la definición como mediante `TipoToken.__members__`. Por ello, `TipoToken.TRY`, `TipoToken.CATCH` y `TipoToken.THROW` no eran nombres alternativos válidos: eran accesos a atributos inexistentes del enum y podían provocar `AttributeError` al evaluarse esas rutas del parser o las construcciones manuales del test.

## 4. Contrato del lexer

Las reglas vigentes del lexer son:

| Lexema reconocido | Token emitido |
| --- | --- |
| `try` | `TipoToken.INTENTAR` |
| `intentar` | `TipoToken.INTENTAR` |
| `catch` | `TipoToken.CAPTURAR` |
| `capturar` | `TipoToken.CAPTURAR` |
| `throw` | `TipoToken.LANZAR` |
| `lanzar` | `TipoToken.LANZAR` |

Las expresiones regulares aparecen como reglas separadas para las formas inglesa y española, pero convergen en un solo tipo por concepto. Una comprobación ejecutable sobre los seis lexemas confirmó las seis correspondencias. El contrato, por tanto, ya normalizaba correctamente ambas grafías antes de que el parser consumiera los tokens.

## 5. Parser antes de #3582

La inspección de `src/pcobra/cobra/core/parser.py` en la base `0f49b7367b80877e395677e85c9a61813664b4d4` muestra estas condiciones:

```python
self.token_actual().tipo in (TipoToken.TRY, TipoToken.INTENTAR)
```

La lista de delimitadores del bloque `try` incluía simultáneamente `TipoToken.CATCH` y `TipoToken.CAPTURAR`, y la condición de entrada al bloque de captura repetía esa pareja. `declaracion_throw` usaba:

```python
self.token_actual().tipo in (TipoToken.THROW, TipoToken.LANZAR)
```

`TRY`, `CATCH` y `THROW` no existían en el enum de esa base. No eran necesarios para admitir los textos ingleses: el lexer ya convertía esos textos a `INTENTAR`, `CAPTURAR` y `LANZAR`. Al evaluar las tuplas, Python debía resolver primero los atributos inválidos, de modo que la presencia adicional del miembro canónico no protegía la ruta. Esto constituía una desalineación real en código de producción, no únicamente una expectativa obsoleta del test.

## 6. Parser después de #3582

En el SHA auditado, `ClassicParser.declaracion_try_catch`:

- compara la entrada únicamente con `TipoToken.INTENTAR`;
- delimita el bloque `try` con `TipoToken.CAPTURAR` (además de los delimitadores estructurales `FIN` y `EOF`);
- reconoce el bloque de captura únicamente con `TipoToken.CAPTURAR`.

Asimismo, `ClassicParser.declaracion_throw` compara únicamente con `TipoToken.LANZAR`. Ya no hay referencias a `TipoToken.TRY`, `TipoToken.CATCH` ni `TipoToken.THROW` en esas rutas. Los mensajes que mencionan las dos grafías siguen siendo compatibles con los lexemas admitidos; no implican dos miembros del enum.

## 7. Test actualizado

En `tests/unit/test_try_catch.py`, el caso que construye tokens a mano cambió solamente sus tipos:

- `Token(TipoToken.TRY, "try")` pasó a `Token(TipoToken.INTENTAR, "try")`;
- `Token(TipoToken.THROW, "throw")` pasó a `Token(TipoToken.LANZAR, "throw")`;
- `Token(TipoToken.CATCH, "catch")` pasó a `Token(TipoToken.CAPTURAR, "catch")`.

Los valores textuales `"try"`, `"throw"` y `"catch"` se conservaron. Esto reproduce correctamente la salida real del lexer: el valor del lexema puede permanecer en inglés mientras `Token.tipo` identifica la categoría canónica española.

## 8. Modelo de aliases textuales

El modelo observado es **alias textual inglés → token canónico español**. El alias pertenece al reconocimiento léxico, no al espacio de nombres de `TipoToken`:

```text
try      ─┐
intentar ─┴─> INTENTAR
catch    ─┐
capturar ─┴─> CAPTURAR
throw    ─┐
lanzar   ─┴─> LANZAR
```

Por ello no se debe inferir `TipoToken.TRY` a partir de que el texto `try` sea válido. Lexema y nombre de enum cumplen funciones diferentes: el lexer acepta variantes superficiales y entrega al parser una representación normalizada.

## 9. Causa raíz

La causa raíz fue una **desalineación lexer/parser en la representación interna de aliases**. El lexer ya cumplía el contrato de normalización y emitía exclusivamente los tokens canónicos españoles para las grafías inglesas y españolas. El parser, en cambio, intentaba admitir las grafías inglesas una segunda vez mediante miembros de enum inexistentes. El test manual replicaba esa misma suposición incorrecta.

No corresponde clasificar el hallazgo como un simple test obsoleto: las referencias inválidas también estaban en `parser.py` y afectaban las rutas productivas de `try/catch/throw`.

## 10. PR #3582

La PR [#3582](https://github.com/Alphonsus411/pCobra/pull/3582), titulada **Use canonical tokens in try/catch parser**, quedó fusionada el 2026-09-15 a las 17:37:28 UTC.

Trazabilidad comprobada:

- base: `0f49b7367b80877e395677e85c9a61813664b4d4`;
- head: `c7dfd193055d8d01421048448bbc34f9c0e88a23` (`Fix canonical try catch parser tokens`);
- merge: `0e8d59d618e6072f3b99de2231a718f1e4bd4a0f`;
- archivos modificados: `src/pcobra/cobra/core/parser.py` y `tests/unit/test_try_catch.py`;
- magnitud: 6 inserciones y 7 eliminaciones.

El cambio eliminó del parser las alternativas inválidas `TRY`, `CATCH` y `THROW`, dejando las comparaciones canónicas, y alineó los tokens creados manualmente en el test. El diff base–head confirma que #3582 **no modificó el lexer, la definición del enum ni el AST**. No añadió aliases al enum ni alteró reglas léxicas.

## 11. Pruebas focales

Se ejecutaron únicamente comprobaciones relacionadas con el hallazgo:

1. `pytest -q tests/unit/test_try_catch.py` — **falló: 2 passed, 4 failed**. Los dos tests de intérprete pasaron. Los cuatro fallos son residuos independientes ya conocidos: dos aserciones `isinstance` por identidad/repr de clases AST y dos rechazos de `NodoTryCatch` por `constant_folder`. No hubo un fallo que indicara la reaparición de `TipoToken.TRY`, `CATCH` o `THROW`; en los casos del parser este alcanzó a construir un `NodoTryCatch` antes de la aserción de identidad.
2. `pytest -q tests/unit/test_try_catch.py::test_interpreter_try_catch tests/unit/test_try_catch.py::test_interpreter_intentar_lanzar_capturar` — **2 passed**.
3. Una comprobación con `PYTHONPATH=src python` tokenizó individualmente `try`, `intentar`, `catch`, `capturar`, `throw` y `lanzar`, comparó cada resultado con su miembro canónico y comprobó la ausencia de `TRY`, `CATCH` y `THROW` en `TipoToken.__members__` — **correcta**.

También se intentó seleccionar `test_lexer_finalmente_keyword` junto a un test existente, pero ese nombre no existe en el archivo y pytest terminó con código 4 sin ejecutar pruebas. Fue un error de selección de auditoría, no evidencia de producto ni un fallo que deba corregirse en esta tarea.

La suite completa no está verde y este informe no afirma lo contrario. Los fallos independientes se registran sin modificarlos.

## 12. Estado de Runtime Stabilization Contract

Para el head `c7dfd193055d8d01421048448bbc34f9c0e88a23`, GitHub Actions registra el workflow **Runtime Stabilization Contract** como `completed / success` (run `34999177456`; job `runtime-stabilization-contract` `completed / success`). El merge `0e8d59d618e6072f3b99de2231a718f1e4bd4a0f` también registra ese workflow como `completed / success` (run `35002429941`).

Esto no equivale a CI global verde. Para el head hubo workflows `Lint`, `tests`, `CI` y `CodeQL` con conclusión `failure`, además de `Label PRs by branch` en `failure`; varios jobs de sus matrices fallaron, fueron cancelados o se omitieron. Para el merge también constan fallos independientes en `CodeQL`, `Lint`, `Deploy Docs`, `Build & Release CLI Binaries`, `CI` y `tests`. Esos resultados no se investigan ni se atribuyen a Task 7.

## 13. Clasificación final

**DESALINEACIÓN LEXER/PARSER — CORREGIDA**

La clasificación se sostiene porque:

- el lexer ya aceptaba los aliases textuales ingleses;
- emitía para ellos los tokens canónicos españoles;
- el parser aún referenciaba miembros inexistentes del enum;
- #3582 eliminó esas referencias del parser y del test manual;
- el contrato quedó alineado sin crear aliases en `TipoToken`;
- no fue necesario modificar el lexer.

## 14. Problemas independientes fuera de alcance

Se dejan expresamente separados, sin investigación ni corrección:

- la discrepancia `TipoToken.DEFER` / `TipoToken.APLAZAR`;
- problemas de identidad o representación (`repr`) de clases AST;
- fallos de `constant_folder` frente a estructuras AST;
- LarkParser / `UnexpectedCharacters`;
- cualquier workflow fallido ajeno al contrato focal;
- cualquier otro alias histórico que pudiera detectarse.

Ninguno de esos residuos cambia la conclusión específica sobre `TRY`, `CATCH` y `THROW`, y ninguno debe mezclarse con el cierre de Task 7.

## 15. Conclusión

`TipoToken.TRY`, `TipoToken.CATCH` y `TipoToken.THROW` no pertenecen al enum vigente. Los tokens canónicos son `TipoToken.INTENTAR`, `TipoToken.CAPTURAR` y `TipoToken.LANZAR`. Los lexemas ingleses `try`, `catch` y `throw` siguen siendo aliases válidos a nivel lexer, igual que sus formas españolas, pero todos se normalizan a esos miembros canónicos.

El parser estaba desalineado respecto del lexer porque referenciaba enums inexistentes pese a recibir ya la representación normalizada. La PR #3582 corrigió esa desalineación eliminando las referencias inválidas y ajustando el test manual, sin modificar el lexer ni añadir miembros al enum. Con la evidencia histórica, focal y de Actions registrada, Task 7 puede cerrarse como:

**DESALINEACIÓN LEXER/PARSER — CORREGIDA**
