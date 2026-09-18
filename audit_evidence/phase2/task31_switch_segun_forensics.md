# Task 31 — Forense de `switch` / `segun`

## Alcance y método

Esta microtarea es exclusivamente forense. Se partió de
`fa195c483d13da84ba2f5dd10b2d2f9180fe5a2a`, con el árbol limpio, y no se
modificaron Lexer, Parser, tests, tooling ni documentación normativa. Las
conclusiones siguientes describen el contrato observable; no implementan una
política nueva.

Se inspeccionaron `TipoToken`, Lexer, Parser, `PALABRAS_RESERVADAS`, el lexer
Pygments del REPL, la gramática TextMate de VS Code, snippets, EBNF, SPEC,
Libro, README, documentación secundaria, tests, ejemplos, transpiladores e
historia Git. Además de la lectura estática se ejecutaron sondas con las clases
reales (`PYTHONPATH=src python`) y la prueba dirigida existente.

## Evidencia de implementación

### Enum, Lexer y palabras reservadas

`TipoToken` contiene `SWITCH = "SWITCH"` y no contiene un miembro `SEGUN`.
Esto solamente muestra normalización interna, no una preferencia normativa.
La especificación del Lexer asocia el patrón `\b(switch|segun)\b` a
`TipoToken.SWITCH`.

Las sondas reales dieron:

```text
Lexer("switch") -> [(SWITCH, "switch"), (EOF, None)]
Lexer("segun")  -> [(SWITCH, "segun"),  (EOF, None)]
hasattr(TipoToken, "SEGUN") -> False
"switch" in PALABRAS_RESERVADAS -> True
"segun"  in PALABRAS_RESERVADAS -> True
```

Por tanto, se conserva el lexema original en `Token.valor`, pero ambos lexemas
comparten tipo. `PALABRAS_RESERVADAS` contiene expresamente ambos, de modo que
ninguno queda disponible como identificador ordinario.

### Parser y AST

Se analizaron exactamente estos programas, cambiando únicamente la primera
palabra:

```cobra
switch x:
    case 1:
        pasar
fin
```

```cobra
segun x:
    case 1:
        pasar
fin
```

Ambos parsearon sin errores ni advertencias del Parser y sin warnings de
Python. En ambos casos el despacho de `TipoToken.SWITCH` fue
`declaracion_switch`; este handler consume `SWITCH` sin consultar
`Token.valor`. Los dos resultados tuvieron la misma representación estructural:

```text
NodoSwitch(
  expresion=NodoIdentificador("x"),
  casos=[NodoCase(
    valor=NodoPattern(NodoValor(1)),
    cuerpo=NodoBloque([NodoPasar()])
  )],
  por_defecto=NodoBloque([])
)
```

La comparación recursiva de tipo de nodo y atributos dio `True`. El AST no
retiene si la cabecera fue `switch` o `segun`.

### REPL/Pygments, VS Code y snippets

La ejecución de `pygments.lex` con el `CobraLexer` real produjo
`Token.Keyword` para `switch` y para `segun`. No es sólo una consecuencia
inferida de la regex: ambas sondas devolvieron esa categoría.

La gramática TextMate contiene ambas alternativas en el patrón real de
`keyword.control.cobra`: `...|switch|segun|...`. Son alternativas delimitadas
por palabra, no coincidencias incidentales. El único fichero de snippets Cobra,
`extensions/vscode/snippets/cobra.json`, ofrece función, condicional y bucle
`para`; no ofrece snippet para esta construcción y no contiene ninguna de las
dos formas. Esa ausencia no decide la política.

### Transpiladores

Los transpiladores públicos de Python, JavaScript y Rust registran visitantes
`visit_switch` que reciben un `NodoSwitch`. Sus pruebas de generación
construyen `NodoSwitch` manualmente. Como el AST normalizado no conserva el
lexema de cabecera, esos backends no pueden diferenciar `switch` de `segun` y
no aportan evidencia de canonicidad fuente. Las apariciones de `switch` en el
JavaScript generado o en nombres de módulos backend tampoco son sintaxis
fuente Cobra.

## Evidencia de superficies documentales

### EBNF

La producción actual de `docs/gramatica.ebnf` es exactamente:

```ebnf
switch: "switch" expr ":" case+ ("sino" ":" cuerpo)? "fin"
```

La regla `statement` referencia el no terminal `switch`, pero no existe otra
aparición de `segun`. La EBNF enseña únicamente `switch`.

### SPEC

En `docs/SPEC_COBRA.md` se distinguen cuatro superficies:

* **Producción:** `switch: "switch" expr ":" case+ "fin"`; sólo `switch`.
* **Lista de keywords:** enumera `switch`, `case`; no `segun`.
* **Ejemplo fuente:** el bloque de control de flujo comienza con
  `switch valor:`; no hay ejemplo con `segun`.
* **Narrativa:** no define `segun` como alias, forma canónica, compatibilidad ni
  deprecación. Las demás apariciones de «switch» fuera de sintaxis no alteran
  esta conclusión.

La SPEC enseña consistentemente `switch`, aunque su producción omite además el
bloque `sino` que sí aparece en EBNF/Parser; esa diferencia lateral no se
resuelve aquí.

### Libro normativo

`docs/LIBRO_PROGRAMACION_COBRA.md`, fuente normativa indicada por el
repositorio, contiene `switch` en el índice autogenerado de tokens, estructuras
y sentencias. No contiene `segun` como palabra completa. La única aparición
adicional relevante de «Switch» es una mención de interfaz («Switch de
transpilación»), no sintaxis fuente. El Libro presenta `switch` como nombre
incluido en el lenguaje, pero no dice explícitamente «forma canónica», no
documenta la producción completa aquí y no caracteriza ni rechaza `segun`.

Así, el Libro demuestra que `switch` es normativo; no demuestra por sí solo si
`segun` es alias público, compatibilidad histórica o residuo.

### README y documentación secundaria

* `README.md` documenta explícitamente el token `SWITCH` como «Palabra clave
  `switch` o `segun`». Es documentación pública de ambas grafías, aunque no es
  la fuente normativa superior.
* `docs/README.en.md` contiene la misma tabla en inglés: `Keyword "switch" or
  "segun"`.
* `docs/especificacion_tecnica.md` enseña una construcción «Switch ampliado» y
  un ejemplo `switch x:`; no menciona `segun`.
* `CORE_AUDIT_PHASE1.md` registró `segun` como alias y `switch` como forma
  documentada multi-backend. Es evidencia histórica de una clasificación de
  auditoría, no una decisión normativa vigente.
* Informes forenses previos de fase 2 describen la normalización funcional y la
  divergencia, pero tampoco contienen una decisión normativa vinculante.
* El resto de coincidencias revisadas se refiere a widgets GUI, `git switch`,
  módulos o salida JavaScript, o al adverbio español «según» escrito sin tilde;
  no constituye sintaxis fuente.

### Ejemplos públicos

La búsqueda por palabra completa, sin distinguir mayúsculas, en `examples/` no
encontró programas públicos que usen `switch` ni `segun`. Por ello los ejemplos
no favorecen ninguna política. La ausencia tampoco contradice el Libro, la
SPEC o el comportamiento ejecutable.

## Evidencia de tests

La cobertura observada se separa así:

* **Léxica:** `tests/test_lexer_parser_contract.py` exige expresamente que
  `switch` y `segun` produzcan `TipoToken.SWITCH`; también incluye ambos en la
  lista de palabras cuya tokenización se comprueba.
* **Parser E2E positivo:** `tests/unit/test_parser_switch.py` analiza programas
  fuente con `switch` y comprueba `NodoSwitch`, casos, patrón y guardia.
* **Consistencia AST:** `tests/unit/test_parser_consistencia_ast.py` usa fuente
  con `switch`.
* **Parser E2E con `segun`:** no se encontró uno en la suite vigente. La sonda
  forense de esta tarea confirma que funciona, pero no modifica la suite.
* **Equivalencia explícita de ambos AST:** no existe un test dedicado en la
  suite; la sonda de esta tarea sí obtuvo igualdad estructural.
* **Transpiladores:** las pruebas de Python, JavaScript y Rust construyen
  `NodoSwitch` manualmente; prueban generación desde AST, no una grafía fuente.
* **Negativos/snapshots:** no se encontró ningún test que espere el rechazo de
  `segun`, ni snapshot fuente que establezca esa política.

En respuesta breve: los E2E existentes enseñan `switch`; la aceptación de
`segun` está protegida a nivel léxico, pero no por un E2E de Parser.

## Historia Git relevante

La historia disponible tiene un límite material: los commits antiguos se
presentan como raíces injertadas (`grafted`). `git blame` atribuye en bloque el
enum `SWITCH`, el patrón `(switch|segun)`, ambas entradas de reservadas y otras
superficies al snapshot `4ea8897` (merge de PR #3322, 2026-07-18). Ese commit ya
contiene las dos formas; su asunto trata de `usar_loader`, no explica su
introducción ni una política de aliases. El siguiente gran snapshot revisado,
`a55548f` (merge de PR #3495, 2026-08-16), también las contiene.

Las búsquedas `git log -S'segun'` y `git log -S'TipoToken.SWITCH'` sobre las
superficies relevantes no descubrieron, en la historia accesible anterior al
snapshot, un commit de introducción con motivación. Tampoco se halló mensaje de
commit o texto vigente que declare deprecación, migración de `switch` a
`segun`, migración inversa o plazo de retirada.

Sí existe evidencia explícita de que el repositorio **denomina** alias a
`segun`: `CORE_AUDIT_PHASE1.md` dice «alias `segun`» y «alias histórico no
descrito por el Libro». Sin embargo, por instrucción de esta auditoría esa
conclusión antigua no es autoridad normativa final, y la historia accesible no
permite demostrar que `segun` **se añadiera** mediante un commit como alias ni
con qué promesa de compatibilidad. La tabla pública del README («`switch` o
`segun`») sí demuestra documentación pública de ambas grafías, pero no asigna
canonicidad.

## Matriz contractual

| Forma | Core | Parser | Reservadas | REPL | VS Code | EBNF | SPEC | Libro | Tests | Historia |
|---|---|---|---|---|---|---|---|---|---|---|
| `switch` | `SWITCH`; conserva valor `switch` | `declaracion_switch`; `NodoSwitch` | Sí | `Keyword` | `keyword.control.cobra` | Única literal de cabecera | Producción, keyword y ejemplo | Incluida como token/estructura/sentencia | E2E Parser positivo, consistencia AST y cobertura léxica | Ya presente en snapshots accesibles; auditoría previa la llama documentada |
| `segun` | `SWITCH`; conserva valor `segun`; no hay token `SEGUN` | Mismo handler y AST, sin warnings | Sí | `Keyword` | `keyword.control.cobra` | Ausente | Ausente | Ausente | Cobertura léxica positiva; sin E2E Parser ni equivalencia dedicada; ningún rechazo | Ya presente en snapshots; auditoría previa la llama alias, pero no se recuperó commit de introducción/motivación |

## Respuestas forenses obligatorias

1. **¿`switch` funciona actualmente?** Sí: tokeniza, parsea y produce
   `NodoSwitch` sin errores ni advertencias.
2. **¿`segun` funciona actualmente?** Sí, con el mismo resultado observable.
3. **¿Ambos generan el mismo token?** Sí, `TipoToken.SWITCH`; sólo difiere
   `Token.valor` (`switch` frente a `segun`).
4. **¿Ambos alcanzan el mismo handler?** Sí, el despacho por tipo llama a
   `declaracion_switch`.
5. **¿Ambos producen el mismo AST?** Sí; la comparación estructural recursiva
   fue verdadera y el lexema no queda en el nodo.
6. **¿Ambos están reservados?** Sí, ambos son miembros exactos de
   `PALABRAS_RESERVADAS`.
7. **¿Ambos están resaltados en REPL?** Sí, como `Token.Keyword` por el
   `CobraLexer` real.
8. **¿Ambos están resaltados en VS Code?** Sí, como alternativas reales de
   `keyword.control.cobra`.
9. **¿Qué forma enseña EBNF?** Sólo `switch`.
10. **¿Qué forma enseña SPEC?** Sólo `switch` en producción, lista y ejemplo.
11. **¿Qué forma enseña el Libro?** `switch`; no contiene `segun` como término
    fuente.
12. **¿Qué forma usan los tests E2E?** `switch`. `segun` sólo tiene contrato
    léxico; no hay E2E positivo vigente con esa cabecera.
13. **¿Hay evidencia histórica explícita de que `segun` se añadiera como
    alias?** No en commits recuperables: el primer snapshot accesible ya lo
    contiene. Una auditoría anterior lo etiqueta como alias, y README lo
    documenta como alternativa, pero ninguna prueba recuperada explica el acto
    de introducción.
14. **¿Hay evidencia de deprecación de alguno?** No.
15. **¿Existe una forma canónica demostrable?** `switch` es la única forma
    normativa demostrable en Libro/SPEC/EBNF y la usada por E2E; no está
    demostrado si esa exclusividad significa canonicidad con compatibilidad o
    mera omisión de `segun`.
16. **¿Hay una simple omisión documental o una política ambigua?** Política
    ambigua. Core, herramientas y README hacen pública la alternativa, mientras
    las tres superficies normativas sólo enseñan `switch`, sin declarar el
    estatuto de `segun`.
17. **¿Es segura una reparación documental directa?** No. Añadir `segun` a las
    superficies normativas impondría Política A; etiquetarlo como compatibilidad
    impondría B; omitirlo conscientemente o retirarlo impondría D. La evidencia
    no autoriza elegir entre ellas.
18. **¿Qué archivos afectaría?** Después de una decisión, probablemente
    `docs/LIBRO_PROGRAMACION_COBRA.md`, `docs/SPEC_COBRA.md` y
    `docs/gramatica.ebnf`; según la política también README/docs secundarios,
    snippets y tests contractuales/E2E. Lexer, Parser, reservadas, REPL y
    TextMate ya son coherentes entre sí para aceptar ambas.
19. **¿Qué archivos NO deben tocarse?** En esta tarea, todos salvo este informe.
    En una eventual reparación sólo documental no deben tocarse Lexer, Parser,
    AST ni transpiladores; tampoco deben alterarse tests o ejemplos para ocultar
    el comportamiento. Cualquier retirada funcional requeriría otra tarea y
    autorización explícita para Lexer/Parser.
20. **¿Cuál debe ser la siguiente Task?** **DECISIÓN NORMATIVA**, para fijar si
    el contrato deseado es A, B o D antes de editar documentación o runtime.

## Clasificación

**F — EVIDENCIA INSUFICIENTE / REQUIERE DECISIÓN NORMATIVA**

Se descartan A, B, C y D como hechos demostrados: A tiene apoyo funcional y en
README, pero contradice la omisión normativa; B encaja con el patrón observado,
pero ninguna fuente vigente declara compatibilidad histórica; C carece de apoyo
normativo porque todas las fuentes normativas enseñan `switch`; D no explica
que reservadas, REPL, VS Code, contrato léxico y README expongan `segun`. También
se descarta E: no es seguro tratar la divergencia como reparación mecánica sin
decidir primero qué promesa pública expresa la aceptación actual.

## SIGUIENTE MICROTAREA RECOMENDADA

Clasificación: F — EVIDENCIA INSUFICIENTE / REQUIERE DECISIÓN NORMATIVA
Confianza: ALTA sobre el estado técnico y la divergencia; MEDIA sobre intención histórica por historia injertada
Riesgo: ALTO si se documenta, degrada o retira una forma sin fijar primero su estatuto público
Política demostrada: Ninguna entre A–D; sólo está demostrada la aceptación técnica bilingüe y la enseñanza normativa exclusiva de `switch`
Cambio recomendado: Adoptar explícitamente A, B o D mediante decisión normativa; sólo después abrir una microtarea separada de reparación coherente
Archivos probablemente afectados: `docs/LIBRO_PROGRAMACION_COBRA.md`, `docs/SPEC_COBRA.md`, `docs/gramatica.ebnf` y, según la decisión, README, docs secundarios, snippets y tests contractuales/E2E
Archivos prohibidos: En la siguiente decisión, Lexer, Parser, AST, transpiladores, ejemplos y tests; no cambiar comportamiento antes de una tarea autorizada específica
Tipo de siguiente tarea: DECISIÓN NORMATIVA
