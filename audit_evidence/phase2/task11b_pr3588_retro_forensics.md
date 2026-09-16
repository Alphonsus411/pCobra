# Phase 2 / Task 11b — Forense retrospectivo de la PR #3588

Fecha de auditoría: 2026-09-16. Esta tarea es exclusivamente documental: no
modifica ni propone modificar en este cambio el lexer, el parser, tests o código
de producción.

## 1. Identificación y alcance

| Dato | SHA / valor |
|---|---|
| Base auditada de la PR #3588 | `21f26acf30a95d26feccb7252a1a4048eaae0e7f` |
| Head de la PR #3588 | `b07d8c977ff0add326fd0eb9bba419a5dc3b0fd2` |
| Merge / `master` auditado | `f9feb8f72d8b4bb48cc58e0b42a92a561f4b7db2` |
| PR | [#3588](https://github.com/Alphonsus411/pCobra/pull/3588), «Retirar aliases ingleses del lexer Pygments del REPL» |

La PR tuvo un commit, 19 adiciones, 2 eliminaciones y dos archivos afectados:
`src/pcobra/cobra/cli/repl/cobra_lexer.py` y
`tests/cli/test_repl_cobra_lexer_contract.py`. El diff exacto eliminó únicamente
`(TipoToken.CON, r"\bwith\b", Keyword)` y
`(TipoToken.COMO, r"\bas\b", Keyword)` y creó un test de 19 líneas que exige
`Keyword` para `con`/`como` y `Name` para `with`/`as`.

La motivación declarada fue alinear el resaltado con
`docs/LIBRO_PROGRAMACION_COBRA.md`, evitar aliases ingleses no presentes en los
tokens actuales y no tocar el frontend core. La descripción de la PR afirmó que
el Libro enumera `con` y `como` y no define `with`/`as`. Esa lectura del estado
normativo **actual** es correcta, pero la motivación no investigó el contrato
histórico descrito en las secciones siguientes.

### Pruebas declaradas en #3588

La PR reportó:

- `pytest -q tests/cli/test_repl_cobra_lexer_contract.py`: 1 passed.
- Cinco módulos contractuales de REPL: 142 passed y 3 fallos preexistentes en
  `tests/integration/test_repl_usar_entrypoints_contract.py`, relativos a
  mensajes runtime de `usar` y ajenos al cambio.
- El mismo conjunto sin ese módulo: 50 passed.
- `ruff`, `python -m py_compile` y comprobación de que no se tocaron rutas core:
  correctos.

La revisión automática dejó un hallazgo P1 independiente: la modificación del
lexer Pygments contravenía la regla de `AGENTS.md` que exigía autorización
explícita y específica para tocar un lexer. No discutió la semántica histórica.
La PR fue fusionada pese a ese comentario.

## 2. Estado inmediatamente anterior y posterior

Las observaciones core y parser son iguales en ambos extremos de #3588; el
único cambio funcional fue la clasificación Pygments del REPL.

| Entrada | Core antes | REPL antes | REPL después | Parser |
|---|---|---|---|---|
| `con` | `TipoToken.CON` | `Keyword` | `Keyword` | Inicia `declaracion_con`; acepta `con recurso como r: pasar fin`. |
| `with` | `TipoToken.IDENTIFICADOR` | `Keyword` (mapeado conceptualmente a `TipoToken.CON`) | `Name` | No inicia `declaracion_con`; una sentencia `with ...` falla. |
| `como` | `TipoToken.COMO` | `Keyword` | `Keyword` | Se acepta como alias de recurso dentro de `con`. |
| `as` | `TipoToken.IDENTIFICADOR` | `Keyword` (mapeado conceptualmente a `TipoToken.COMO`) | `Name` | No se acepta en la posición de `como`; `con recurso as r...` falla. |

El enum de `TipoToken` en la base y el merge contiene `CON` y `COMO`, pero no
`WITH` ni `AS`. El lexer core sólo tiene patrones para `con` y `como`. El parser
sólo despacha `TipoToken.CON` y sólo consume `TipoToken.COMO` en esta
construcción. Por tanto, justo antes de #3588 el REPL **no ejecutaba**
`with/as`: `CobraLexer` es un `RegexLexer` de Pygments usado para colorear; el
pipeline de ejecución vuelve a tokenizar con el lexer core. Sí existía una
divergencia visible: coloreaba como sintaxis palabras que la ejecución trataba
como identificadores y no podía parsear como sentencia de contexto.

Además, `src/pcobra/cobra/core/utils.py` todavía incluye `with` y `as` en
`PALABRAS_RESERVADAS`. Es un vestigio histórico: no las convierte en tokens,
pero puede impedir ciertos usos como nombres. Refuerza que la retirada previa
del alias core no fue una limpieza transversal completa.

## 3. Historia Git: origen deliberado, no copia accidental

La historia completa (fue necesario completar el clon shallow) permite fechar
y explicar el soporte:

1. El commit `48ae0e06366466a67a7d004333a449c20e768521`, fusionado por la
   [PR #725](https://github.com/Alphonsus411/pCobra/pull/725) el 2025-08-06,
   se tituló literalmente **«feat: soportar with/as como alias de con/como»**.
   Añadió juntos:
   - `TipoToken.WITH` y `TipoToken.AS`;
   - patrones core para `with` y `as`;
   - despacho y consumo de ambos tokens en el parser;
   - ambas grafías en palabras reservadas;
   - la gramática EBNF `("with"|"con") ... (("as"|"como") ...)?`;
   - tests positivos de lexer y parser con
     `with recurso as r: pasar fin`.
2. El cuerpo de #725 dijo explícitamente «admite `with`/`as` además de
   `con`/`como`», «documenta y prueba ambas variantes», y registró una ejecución
   dirigida de cuatro tests. Esto demuestra compatibilidad deliberada y pública,
   no una mera conveniencia visual ni una copia fortuita de Python.
3. El lexer Pygments nació después, en
   `3a425d50abe2795678dd31859d097222957da58d` (2025-08-10), con reglas
   `TipoToken.WITH`/`TipoToken.AS`. Es decir, reflejó soporte core ya existente;
   no originó la política.
4. El commit directo
   `193c2d792ec1144f89b5ecdb878178f2b3af6402` (2026-06-14),
   «refactor: standardize token and keyword names to Spanish», eliminó los enums
   y patrones ingleses y las ramas correspondientes del parser. En el lexer
   Pygments, sin embargo, cambió `TipoToken.WITH` a `TipoToken.CON` y
   `TipoToken.AS` a `TipoToken.COMO` **sin eliminar las regex inglesas**. Desde
   ese punto el soporte quedó sólo como resaltado, no como ejecución.
5. El test histórico positivo de parser se renombró y cambió a sintaxis española
   en `88f4f311c3fbda7ef4c9154e5667e46f7bed8f7b` (2026-07-28). Ese cambio limpió
   cobertura, pero no contiene una política de deprecación, migración o ruptura.
6. Finalmente #3588 eliminó el vestigio del resaltador. `with` y `as` se
   introdujeron juntos y se retiraron del core juntos; tampoco hay evidencia de
   políticas separadas para cada palabra.

Por ello son falsas, consideradas históricamente, las hipótesis «nunca hubo
`TipoToken.WITH/AS`» y «el core nunca los reconoció». Son ciertas únicamente
para la fotografía de la base de #3588.

## 4. Evidencia documental

### Fuente normativa actual

El Libro actual enumera `como` y `con` entre las palabras clave (líneas 120–121)
y no presenta `with` o `as` como sintaxis Cobra. También exige que toda nueva
palabra clave actualice coherentemente lexer, parser, AST/transpiladores,
documentación y tests. Bajo esa norma actual, la forma canónica es española.

### Documentación histórica y contradicción vigente

- `docs/gramatica.ebnf` conserva hoy
  `with_stmt: ("with"|"con") expr (("as"|"como") IDENTIFICADOR)? ...`. Esa línea
  fue introducida por #725 y nunca revertida. Es documentación de sintaxis, no
  una comparación con Python ni un snippet Python.
- La PR #725 documentó ambas variantes de manera explícita y añadió tests
  ejecutables. Esto constituye evidencia más fuerte que una coincidencia textual.
- README actual describe los tokens `CON` y `COMO` y no promete `WITH`/`AS`.
- Las apariciones de `with`/`as` en salidas esperadas de transpiladores, pruebas
  Python, mensajes o nombres de variables no se contabilizaron como sintaxis
  Cobra. Tampoco se usaron snippets Python ni nombres de tests como prueba por sí
  solos.
- No se localizó en README, changelog/release notes ni documentación del REPL una
  deprecación anunciada de los aliases, una ventana de migración o una decisión
  explícita de compatibilidad que reconciliara #725, el EBNF y el Libro.

En consecuencia, el Libro respalda la forma canónica actual, pero el repositorio
mantiene documentación contractual contradictoria y no documentó adecuadamente
la retirada de una compatibilidad que sí había sido oficial.

## 5. Evidencia de tests y política de aliases

- #725 añadió un test de lexer que exigía `TipoToken.WITH` y `TipoToken.AS`, y un
  test de parser que construía `NodoWith` desde `with recurso as r: pasar fin`.
  Hubo, por tanto, tests históricos explícitos de aceptación core.
- En el estado actual no se encontraron tests core que acepten `with/as` ni un
  test contractual explícito que documente su rechazo. El rechazo se observa al
  ejecutar el pipeline, pero no aparece como política de migración.
- #3588 añadió el primer test focal del resaltador para exigir `Name`; el test
  describe fielmente el nuevo comportamiento, pero su aserción de «sin aliases»
  no estaba respaldada por la historia completa ni por el EBNF vigente.
- El repositorio sí mantiene aliases bilingües deliberados en otros puntos. Por
  ejemplo, el lexer Pygments reconoce `func|definir`, `switch|segun`,
  `case|caso`, `interface|trait`, `try|intentar`, `catch|capturar` y
  `throw|lanzar`. La forma arquitectónica usada es mapear dos grafías al mismo
  `TipoToken`; exactamente esa normalización quedó en el REPL para `with/as`
  tras junio de 2026. Esto no obliga a conservar cada alias, pero demuestra que
  «el lenguaje está en español» no es por sí solo una política general que
  autorice eliminarlos sin revisar cada contrato.

## 6. Respuestas a las preguntas de auditoría

1. **¿Fueron parte oficial?** Sí. #725 los añadió al lexer core, parser, enum,
   palabras reservadas, EBNF y tests positivos.
2. **¿Aliases deliberados?** Sí; título, cuerpo y diff de #725 lo dicen de forma
   inequívoca.
3. **¿Existieron únicamente en Pygments?** No históricamente. Sólo entre
   `193c2d792` y #3588 quedó soporte residual exclusivo de resaltado.
4. **¿El REPL los ejecutaba?** Cuando el core aún los soportaba, el pipeline podía
   ejecutarlos. Inmediatamente antes de #3588 sólo los coloreaba; no los
   ejecutaba.
5. **¿Había divergencia?** Sí, en la base de #3588.
6. **¿La eliminación aproxima el resaltado al core actual?** Sí, localmente y en
   la fotografía actual.
7. **¿Rompe contrato documentado o histórico?** Rompe la continuidad del contrato
   histórico de #725 y contradice el EBNF aún vigente, aunque la capacidad de
   ejecución ya había sido retirada por `193c2d792`.
8. **¿El test está respaldado o inventa política?** Verifica correctamente el
   resultado local, pero eleva a contrato «sin aliases» una política no
   reconciliada con #725, el EBNF y la ausencia de deprecación. No basta como
   justificación retrospectiva.
9. **¿Debe conservarse tal como está?** No. La coherencia puntual con el core no
   compensa la retirada no documentada de una compatibilidad deliberada. La
   decisión final debe tratarse separadamente y de forma coherente en todos los
   componentes; esta auditoría no implementa esa decisión.

## 7. Análisis de compatibilidad

#3588 no originó la pérdida de ejecución: ésta ocurrió en `193c2d792`. Sí retiró
la última conducta compatible del resaltador y consolidó mediante un test una
ruptura que carecía de deprecación y cuya documentación EBNF seguía prometiendo
las grafías inglesas. La divergencia previa era un defecto real, pero tenía dos
soluciones conceptuales (restaurar ejecución o retirar promesa/resaltado); la PR
eligió una sin completar la investigación histórica. Por eso no puede
clasificarse meramente como corrección válida o deuda documental.

## 8. Clasificación final

**PR #3588 INTRODUCE REGRESIÓN DE COMPATIBILIDAD**

La clasificación se limita al contrato del resaltador que #3588 cambió y a la
compatibilidad histórica que consolidó como retirada. No atribuye a #3588 la
regresión core anterior.

## 9. Recomendación

**abrir una tarea separada para revertir #3588**

No se implementa aquí. La tarea separada deberá decidir además, bajo autorización
explícita para lexer/parser, cómo reconciliar la regresión core de junio, el
Libro actual, el EBNF, las palabras reservadas residuales y la política de
deprecación. Revertir únicamente el resaltado restauraría el estado anterior a
#3588, pero no arreglaría por sí solo la ejecución.

## 10. Riesgos residuales

- El contrato normativo actual (Libro) y `docs/gramatica.ebnf` discrepan.
- `PALABRAS_RESERVADAS` conserva `with/as` aunque el lexer los emite como
  identificadores.
- No se auditó aquí si releases publicados entre agosto de 2025 y junio de 2026
  prometieron compatibilidad semántica adicional fuera del repositorio; ello
  podría aumentar, no reducir, el impacto.
- Restaurar sólo Pygments recuperaría color pero mantendría divergencia con la
  ejecución; restaurar el core requeriría una tarea autorizada y pruebas de todos
  los backends.
- Los otros aliases bilingües requieren auditorías individuales: esta conclusión
  no los valida ni los invalida por analogía.

## 11. Archivos y comandos inspeccionados

Se inspeccionaron, en sus revisiones actuales e históricas pertinentes:
`AGENTS.md`, `README.md`, `CHANGELOG.md`, `docs/LIBRO_PROGRAMACION_COBRA.md`,
`docs/gramatica.ebnf`, documentación bajo `docs/`, ejemplos bajo `examples/`,
`src/pcobra/cobra/core/{lexer,parser,utils}.py`,
`src/pcobra/cobra/cli/repl/cobra_lexer.py`, tests de lexer/parser/REPL y los
archivos originales con rutas anteriores a la reorganización del paquete.

Comandos principales (además de lecturas acotadas con `sed` y `rg`):

```text
git show / git diff 21f26ac..b07d8c9
git log --all --follow -S... / git blame 21f26ac -- ...
git fetch --unshallow https://github.com/Alphonsus411/pCobra.git master
git show 48ae0e0 / git show 193c2d792 / git show 88f4f311
rg -n ... README.md docs examples CHANGELOG.md tests src
GitHub REST API: pulls/3588, reviews/comments y pulls/725
PYTHONPATH=src python (sondas de Lexer, Parser y Pygments)
```

La consulta REST fue necesaria porque `gh pr view` no disponía de autenticación.
Completar el historial sólo añadió objetos Git; no cambió el árbol de trabajo.
