# Task 20 — Forense de residuos `in` / `en` en el bucle `para`

## 1. Alcance, base y método

Esta investigación es exclusivamente documental. Se ejecutó sobre
`dff22950150cf236bf8201a1406f0f3ab0bed7de`; al inicio, `git rev-parse HEAD`
devolvió exactamente ese SHA y `git status --short` no produjo salida. No se
modificaron producción, Lexer, Parser, pruebas, documentación normativa,
ejemplos ni extensión.

Se inspeccionaron el enum, Lexer, Parser, Libro, EBNF, especificación,
`PALABRAS_RESERVADAS`, Pygments/REPL, superficies de VS Code, pruebas,
documentación pública, ejemplos y la historia Git disponible. Además se usó
una sonda ejecutable para no inferir el contrato únicamente del texto.

La búsqueda separó expresamente sintaxis Cobra de Python, inglés natural,
APIs y código generado. La tabla de la sección 10 registra **22 referencias o
grupos de referencias relevantes**. Cuando una aparición canónica de `en`
sirve sólo como control negativo (no es un residuo que reparar), se marca F;
esto evita confundir evidencia de coherencia con una promesa de alias `in`.

## 2. Enum, Lexer core y sonda real

En `src/pcobra/cobra/core/lexer.py:17-44`, el enum declara
`EN = "EN"` en la línea 31. No declara un miembro `IN`; la búsqueda de
`TipoToken.IN` en producción es vacía. La sonda sobre
`TipoToken.__members__` confirmó:

```text
EN member True EN
IN member False
```

La tabla de patrones del Lexer contiene exclusivamente
`(TipoToken.EN, re.compile(r"\ben\b"))` en
`src/pcobra/cobra/core/lexer.py:220` y después aplica la regla general de
identificadores. La sonda real `Lexer(texto).tokenizar()` produjo:

```text
en [('EN', 'en'), ('EOF', None)]
in [('IDENTIFICADOR', 'in'), ('EOF', None)]
```

Por tanto, `in` no es una keyword del Lexer core y no es un alias léxico de
`en`.

## 3. Parser y aceptación efectiva

`Parser.declaracion_para()` está en
`src/pcobra/cobra/core/parser.py:384-424`. Después de consumir `PARA` y el
`IDENTIFICADOR` de iteración, comprueba exactamente `TipoToken.EN`
(líneas 396-400), lo consume y sólo entonces procesa la expresión iterable.
No contempla `IN` ni un identificador con valor `in`.

La sonda con programas completos confirmó:

```text
'para x en [1]:' ACCEPT list 1
'para x in [1]:' REJECT ParserError Se esperaba ':' después del iterable en 'para'
```

El texto final del segundo diagnóstico resulta de la recuperación de errores;
no significa aceptación de `in`. La entrada fue rechazada y no produjo AST.

## 4. Fuente normativa principal

El Libro prescribe la forma española. En §4.3 usa
`para nombre en nombres:` (`docs/LIBRO_PROGRAMACION_COBRA.md:638-644`) y en
§4.4 usa `para n en [1,2,3,4,5]:`
(`docs/LIBRO_PROGRAMACION_COBRA.md:646-654`). Esos ejemplos coinciden con el
Lexer y el Parser.

Sin embargo, su índice de palabras clave todavía enumera `in` en
`docs/LIBRO_PROGRAMACION_COBRA.md:141` y no enumera `en` en ese listado. Esa
línea es documentación obsoleta (B), no evidencia normativa suficiente para
crear un alias: contradice tanto los ejemplos específicos del propio Libro
como el contrato ejecutable.

## 5. EBNF y especificación secundaria

`docs/gramatica.ebnf:30` conserva:

```ebnf
bucle_para: "para" IDENTIFICADOR "in" expr ":" cuerpo "fin"
```

Es documentación obsoleta (B): contradice el Parser y los ejemplos normativos
del Libro, pero el archivo no participa en la ejecución observada.

`docs/SPEC_COBRA.md` tiene una contradicción interna equivalente: la producción
de la línea 34 prescribe `in` y la lista de palabras clave de la línea 73 lo
presenta como keyword, mientras su ejemplo de control de flujo de la línea 157
usa `para var i en rango(5):`. Las dos primeras referencias son B; el ejemplo
con `en` es un control coherente F.

## 6. `PALABRAS_RESERVADAS`

En `src/pcobra/cobra/core/utils.py:33-95`, el conjunto contiene `"in"` en la
línea 53 y **no contiene `"en"`**. Conceptualmente, este registro auxiliar
presenta `in` como nombre reservado aunque el Lexer lo entrega como
`IDENTIFICADOR`, y omite la keyword que el Lexer sí reconoce. Es una
contradicción funcional activa (A) en validaciones de nombres que consultan el
conjunto, pero no vuelve aceptable `para x in iterable` ni crea
`TipoToken.IN`.

## 7. REPL / Pygments

`src/pcobra/cobra/cli/repl/cobra_lexer.py:27-87` asigna `en` a `Keyword`
mediante `TipoToken.EN` en la línea 52. No tiene regla para `in`, por lo que
éste cae en la regla general de identificadores de la línea 87 y se resalta
como `Name`. No hay divergencia `in/en` con el Lexer core en esta superficie.

## 8. Editor y resaltado

La extensión de VS Code es internamente mixta:

- `extensions/vscode/README.md:53-59` enseña `para item en iterable:`;
- `extensions/vscode/snippets/cobra.json:22-29` genera la misma forma `en`;
- `extensions/vscode/syntaxes/cobra.tmLanguage.json:23` incluye `in`, pero no
  `en`, en el patrón `keyword.control.cobra`.

README y snippet son controles coherentes (F). La gramática TextMate sí es A:
interpreta visualmente `in` como keyword Cobra y deja `en` como texto no
keyword, en oposición al Lexer core y al propio snippet.

## 9. Pruebas, documentación pública e historia

### 9.1 Pruebas

No queda ningún `TipoToken.IN` ni test positivo que espere que
`para ... in ...` funcione. `tests/test_lexer_parser_contract.py:48-100`
incluye `"en": TipoToken.EN` en la línea 81 y no incluye `in`.

Hay exactamente dos fragmentos Cobra de prueba con `para ... in ...`:

1. `tests/unit/parser_error_handling.py:11-14`: exige `ParserError` para una
   entrada inválida; es D. La entrada también carece de `:`, pero el uso de
   `in` no expresa una expectativa de aceptación.
2. `tests/unit/test_parser_block_contract.py:120-126`: caso parametrizado de
   error que usa `in` y exige el diagnóstico recuperado sobre `:`; es D. La
   prueba focal pasó y confirma que debe conservarse como contraste, aunque una
   tarea futura podría hacer explícito qué defecto pretende aislar sólo si se
   abre una decisión de calidad de tests separada.

El comando focal ejecutado sobre ambos contextos obtuvo `1 passed, 13
deselected`; no se cambió ninguna prueba.

### 9.2 Documentación y ejemplos públicos

Además de EBNF, SPEC y Libro:

- `README.md:769-786` afirma que existe el token `IN`, aunque su ejemplo de la
  línea 898 usa `en`: la tabla es B y el ejemplo es F.
- `docs/README.en.md:463-478` repite `IN | Keyword "in"`: es B.
- Las demás muestras Cobra localizadas usan `en`, entre ellas
  `docs/guia_basica.md:48`, `docs/frontend/caracteristicas.rst:40`,
  `docs/frontend/ejemplos_avanzados.rst:30` y
  `examples/casos_reales/bioinformatica/ejemplo_gc.cobra:4`; se agrupan como F.
- Las apariciones de `in` en bucles Python, código generado, prosa inglesa y
  nombres de API son F y no se cuentan individualmente: no presentan sintaxis
  fuente Cobra.

### 9.3 Historia Git disponible

El repositorio local es superficial: `f33b83a` aparece como raíz injertada.
En la historia verificable, ese snapshot de 2026-07-18 ya contenía
simultáneamente `TipoToken.EN`, la regla léxica `en`, el `in` de EBNF/SPEC,
`PALABRAS_RESERVADAS` y TextMate. Por ello no es responsable afirmar desde
este clon cuándo se introdujo originalmente `en` o si `TipoToken.IN` existió
antes del límite histórico.

Sí se puede reconstruir la corrección posterior de expectativas positivas:

- `828081d` cambió un token manual `TipoToken.IN, "in"` por
  `TipoToken.EN, "en"`;
- `59f22a5` hizo lo mismo en la prueba larga de `para`;
- `c14ccb2` cambió cinco ejemplos positivos `para ... in ...` a `en`, sin
  tocar los casos de rechazo.

La auditoría conservada en
`audit_evidence/phase2/task6_tipo_token_in_forensics.md:90-147` documenta los
PR #3578-#3580 y concluye que no se añadió alias. `CORE_AUDIT_PHASE1.md:180`,
`:211-215` y `:271` caracteriza igualmente `in` como `IDENTIFICADOR`, fuera
de la superficie pública. Todo ello es E: prueba de arrastre histórico, no de
una decisión vigente de mantener un alias funcional.

## 10. Tabla de trazabilidad y clasificación

| Path | Línea/fragmento | Superficie | Uso de `in/en` | Clasificación | Acción futura propuesta |
|---|---:|---|---|---|---|
| `src/pcobra/cobra/core/lexer.py` | 31; enum completo | Enum | Existe `EN`; no existe `IN` | F — control coherente | Ninguna |
| `src/pcobra/cobra/core/lexer.py` | 220 + regla de identificador | Lexer core | `en → EN`; `in → IDENTIFICADOR` | F — control coherente | Ninguna |
| `src/pcobra/cobra/core/parser.py` | 384-400 | Parser | `declaracion_para()` exige `EN` | F — control coherente | Ninguna |
| `docs/LIBRO_PROGRAMACION_COBRA.md` | 638-654 | Norma, bucles | Dos ejemplos `para ... en ...` | F — control coherente | Ninguna |
| `docs/LIBRO_PROGRAMACION_COBRA.md` | 141 | Norma, índice léxico | Enumera `in` y omite `en` | B — DOCUMENTACIÓN OBSOLETA | Task 21: alinear el índice con el contrato normativo, sin inventar alias |
| `docs/gramatica.ebnf` | 30 | Gramática documental | Producción `bucle_para` usa `in` | B — DOCUMENTACIÓN OBSOLETA | Task 21: expresar el separador canónico `en` |
| `docs/SPEC_COBRA.md` | 34 | Gramática documental | Producción `bucle_para` usa `in` | B — DOCUMENTACIÓN OBSOLETA | Task 21: alinearla con Libro/Parser |
| `docs/SPEC_COBRA.md` | 73 | Índice de keywords | Presenta `in` como keyword | B — DOCUMENTACIÓN OBSOLETA | Task 21: alinear inventario léxico |
| `docs/SPEC_COBRA.md` | 157 | Ejemplo público | Usa `para var i en ...` | F — control coherente | Ninguna |
| `src/pcobra/cobra/core/utils.py` | 33-95, en especial 53 | Registro auxiliar | Contiene `in`; no contiene `en` | A — CONTRADICCIÓN FUNCIONAL ACTIVA | Task 21: alinear el registro con Lexer/Parser; no añadir alias |
| `src/pcobra/cobra/cli/repl/cobra_lexer.py` | 52, 87 | Pygments/REPL | `en` es `Keyword`; `in` cae en `Name` | F — control coherente | Ninguna |
| `extensions/vscode/syntaxes/cobra.tmLanguage.json` | 23 | Resaltado VS Code | Marca `in` keyword y omite `en` | A — CONTRADICCIÓN FUNCIONAL ACTIVA | Task 21: alinear resaltado con Lexer core |
| `extensions/vscode/README.md`; `extensions/vscode/snippets/cobra.json` | 56; 25 | Ayuda/snippet VS Code | Enseñan/generan `para ... en ...` | F — control coherente | Ninguna |
| `tests/test_lexer_parser_contract.py` | 48-100 (81) | Contrato Lexer | Espera `en → EN`; no promete `in` | F — control coherente | Ninguna |
| `tests/unit/parser_error_handling.py` | 11-14 | Test negativo | `para i in ...` debe lanzar `ParserError` | D — TEST DE RECHAZO VÁLIDO | Conservar; no reemplazar `in` automáticamente |
| `tests/unit/test_parser_block_contract.py` | 120-126 | Test negativo | Entrada con `in` permanece rechazada | D — TEST DE RECHAZO VÁLIDO | Conservar en Task 21 |
| `README.md` | 769-786 (784) | Documentación pública | Afirma `IN` como token/keyword | B — DOCUMENTACIÓN OBSOLETA | Task 21: corregir la tabla léxica |
| `README.md` | 898 | Ejemplo público | Usa `para ... en ...` | F — control coherente | Ninguna |
| `docs/README.en.md` | 463-478 (476) | Documentación pública inglesa | Afirma `IN` como keyword | B — DOCUMENTACIÓN OBSOLETA | Task 21: corregir la tabla léxica traducida |
| Docs/ejemplo públicos restantes | rutas de §9.2 | Tutoriales/ejemplo | Usan `para ... en ...` | F — control coherente | Ninguna |
| `audit_evidence/phase2/task6_tipo_token_in_forensics.md`; `CORE_AUDIT_PHASE1.md` | 90-147; 180/211-215/271 | Auditoría preservada | Documenta el conflicto y niega alias `in` | E — EVIDENCIA HISTÓRICA | Conservar sin cambios |
| `828081d`, `59f22a5`, `c14ccb2` | diffs Git | Historia de tests | Retiran `IN/in` de casos positivos y preservan negativos | E — EVIDENCIA HISTÓRICA | Conservar; usar como antecedente |

**Resumen A–G (22 filas):** A=2, B=6, C=0, D=2, E=2, F=10, G=0.
No hay test positivo obsoleto (C) ni hallazgo ambiguo (G). Las apariciones
incidentales F adicionales (Python, prosa y APIs) se excluyeron del conteo
fila a fila por no ser residuos de sintaxis Cobra.

## 11. Respuestas obligatorias

1. **¿`TipoToken.IN` existe actualmente?** No. Sólo existe
   `TipoToken.EN` para este separador.
2. **¿`in` tokeniza actualmente como keyword?** No; tokeniza como
   `IDENTIFICADOR`.
3. **¿El parser acepta `para x in iterable`?** No; la sonda real lo rechaza.
4. **¿El parser acepta `para x en iterable`?** Sí; la sonda real produjo un
   AST para un bucle completo.
5. **¿El Libro prescribe `en`?** Sí, en §4.3 y §4.4; su índice aislado de
   keywords conserva además un `in` obsoleto.
6. **¿El EBNF sigue prescribiendo `in`?** Sí, en su línea 30, en conflicto
   con Libro y ejecución.
7. **¿`PALABRAS_RESERVADAS` contiene `in`?** Sí; contiene `in` y omite `en`.
8. **¿El REPL trata `in` como keyword?** No. Pygments marca `en` como
   `Keyword` e `in` como `Name`.
9. **¿Existe alguna superficie pública que todavía enseñe `in` como sintaxis
   válida?** Sí: EBNF y SPEC lo prescriben en la producción del bucle; las
   tablas léxicas de README español/inglés, el índice del Libro y la lista de
   SPEC también lo presentan como keyword. TextMate lo resalta como keyword.
10. **¿Existen tests donde `in` debe conservarse porque prueban rechazo?** Sí,
    los dos tests negativos identificados en §9.1.
11. **¿Hay evidencia de que `in` deba mantenerse como alias funcional?** No.
    La ejecución, el Libro específico, los tests positivos corregidos y las
    auditorías históricas sostienen lo contrario. La historia anterior a
    `f33b83a` no está disponible en este clon superficial, pero ninguna
    evidencia presente respalda un alias vigente.
12. **¿Qué archivos concretos necesitarían una reparación futura?** Sólo los
    siete enumerados en la propuesta de Task 21 siguiente. Lexer, Parser,
    enum, Pygments/REPL, tests, ejemplos válidos y auditorías históricas no la
    necesitan para este hallazgo.

## 12. Propuesta concreta de Task 21 (no implementada)

### Archivos que deberían cambiar y cambio conceptual

1. `docs/LIBRO_PROGRAMACION_COBRA.md`: alinear el índice de palabras clave
   con la forma `en` ya prescrita en §4.3/§4.4.
2. `docs/gramatica.ebnf`: usar el separador canónico `en` en `bucle_para`.
3. `docs/SPEC_COBRA.md`: alinear producción e inventario de keywords; mantener
   intacto su ejemplo ya correcto.
4. `README.md`: reemplazar la afirmación documental del token inexistente
   `IN` por el token real `EN`/lexema `en`.
5. `docs/README.en.md`: aplicar la misma corrección factual a la tabla inglesa.
6. `src/pcobra/cobra/core/utils.py`: alinear `PALABRAS_RESERVADAS` con el
   contrato ejecutable (`en` reservado, `in` no reservado), sin tocar Lexer ni
   Parser y preservando la interfaz pública del conjunto.
7. `extensions/vscode/syntaxes/cobra.tmLanguage.json`: resaltar `en`, no `in`,
   como keyword Cobra.

### Tests mínimos de esa Task

- Sonda/contrato Lexer: `en → TipoToken.EN`, `in → IDENTIFICADOR`.
- Parser: aceptación de `para x en [1]: ... fin` y rechazo de
  `para x in [1]: ... fin`.
- Contrato de `PALABRAS_RESERVADAS`: presencia de `en` y ausencia de `in`.
- Contrato TextMate: `en` está en keywords e `in` no.
- Verificación textual dirigida de EBNF, SPEC, Libro y ambas tablas README.
- Reejecución de los dos tests D para demostrar que los contrastes de rechazo
  se conservaron.

### Archivos que explícitamente NO deben cambiar

- `src/pcobra/cobra/core/lexer.py` y el enum `TipoToken`;
- `src/pcobra/cobra/core/parser.py`;
- `src/pcobra/cobra/cli/repl/cobra_lexer.py`;
- todos los tests actuales, incluidos los dos casos D, salvo añadir nuevos
  tests contractuales mínimos en archivos separados si la Task 21 lo exige;
- ejemplos Cobra que ya usan `en`;
- `extensions/vscode/README.md` y `extensions/vscode/snippets/cobra.json`;
- auditorías y evidencias históricas existentes.

La reparación propuesta es quirúrgica: elimina promesas/interpretaciones
residuales, pero no sustituye indiscriminadamente texto inglés, no crea
`TipoToken.IN` y no incorpora `in` como alias.

## 13. Clasificación global

**RESIDUOS IN/EN CONFIRMADOS — REPARACIÓN QUIRÚRGICA POSIBLE**
