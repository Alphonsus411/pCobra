# Task 22 — Forense de `interface`, `rasgo` y `trait`

## Alcance, base y método

- Repositorio: `Alphonsus411/pCobra`.
- SHA base verificado antes de cualquier cambio: `925cea77c1fcbd8f59a98f900febe391aa5a9f58`.
- Estado inicial: limpio (`git status --short` no produjo salida).
- Alcance: sólo reconstrucción de contrato; no se ha reparado ni alterado lexer, parser, AST, REPL, transpilers, tests, documentación existente o extensión.
- Sondas ejecutadas contra las clases reales con `PYTHONPATH=src`: `TipoToken.__members__`, `Lexer(...).tokenizar()`, `Parser(...).parsear()` y `pygments.lex(..., CobraLexer())`.
- Programa mínimo de parser usado para cada forma: `<forma> I:\n    func m()\nfin\n`. Es el cuerpo mínimo que exige `declaracion_interface`: cero o más firmas `func nombre(parámetros)` y cierre `fin`.

## Resumen ejecutivo

El contrato está desalineado. El lexer core y el parser aceptan completamente `interface` y `rasgo`; `trait` e `interfaz` son identificadores y no abren esta declaración. Sin embargo, `PALABRAS_RESERVADAS` sólo contiene `interface`; el REPL/Pygments resalta `interface` y `trait`, pero no `rasgo`; y VS Code no resalta ninguna de las cuatro. La única guía específica de la construcción, `docs/interfaces.md`, enseña `interface`; Libro, SPEC y EBNF no definen esta sintaxis. `trait` sí tiene un papel correcto y separado como código destino Rust.

La decisión general del mantenedor exige sintaxis fuente española. La evidencia funcional y de tests hace de `rasgo` la candidata española existente, pero la evidencia pública y contractual todavía conserva `interface`. Por ello, la mejor descripción del estado es **Política C — transición incompleta**, con `rasgo` como forma canónica propuesta para una reparación posterior y una decisión explícita de compatibilidad antes de retirar `interface`.

## 1. Enum: inventario exacto

La sonda `repr(TipoToken.__members__)` confirma un único miembro relacionado: `INTERFACE`. No existen miembros `RASGO`, `TRAIT` ni `INTERFAZ`.

Las claves exactas, en el orden de `TipoToken.__members__`, son:

```text
DIVIDIR, MULTIPLICAR, CLASE, ESTRUCTURA, REGISTRO, ENUMERACION, INTERFACE,
DICCIONARIO, LISTA, RBRACE, DEF, EN, LBRACE, FOR, DOSPUNTOS, VAR, FUNC,
METODO, ATRIBUTO, SI, SINO, SINO_SI, GARANTIA, MIENTRAS, PARA, IMPORT,
USAR, EXPORTAR, OPCION, MACRO, HOLOBIT, PROYECTAR, TRANSFORMAR, GRAFICAR,
INTENTAR, APLAZAR, CAPTURAR, LANZAR, ENTERO, FLOTANTE, CADENA, BOOLEANO,
IDENTIFICADOR, ASIGNAR, SUMA, RESTA, MULT, DIV, MAYORQUE, MENORQUE,
MAYORIGUAL, MENORIGUAL, IGUAL, DIFERENTE, Y, O, NO, MOD, LPAREN, RPAREN,
LBRACKET, RBRACKET, COMA, PUNTO, RETORNO, FIN, EOF, IMPRIMIR, HILO,
ASINCRONICO, DECORADOR, GENERAR, ESPERAR, ROMPER, CONTINUAR, PASAR,
AFIRMAR, ELIMINAR, GLOBAL, NOLOCAL, LAMBDA, CON, FINALMENTE, DESDE, COMO,
SWITCH, CASE, VARIABLE, ASIGNAR_INFERENCIA
```

Cada valor es el miembro homónimo, por ejemplo `INTERFACE: <TipoToken.INTERFACE: 'INTERFACE'>`; no hay aliases de Enum ocultos.

## 2. Lexer core: sonda real

| Entrada aislada | Tokens reales (antes de `EOF`) | Valor conservado | Keyword core | `IDENTIFICADOR` |
| --- | --- | --- | --- | --- |
| `interface` | `TipoToken.INTERFACE` | `"interface"` | Sí | No |
| `rasgo` | `TipoToken.INTERFACE` | `"rasgo"` | Sí | No |
| `trait` | `TipoToken.IDENTIFICADOR` | `"trait"` | No | Sí |
| `interfaz` | `TipoToken.IDENTIFICADOR` | `"interfaz"` | No | Sí |

La regla responsable es `\b(interface|rasgo)\b`. Esta es evidencia **A — SINTAXIS COBRA FUNCIONAL ACTUAL** para las dos primeras formas; que las otras dos sean identificadores no constituye una declaración válida.

## 3. Parser extremo a extremo

El despacho de declaraciones asigna exclusivamente `TipoToken.INTERFACE` a `self.declaracion_interface`. El método consume ese mismo token, luego un `IDENTIFICADOR`, `:`, cero o más firmas abstractas iniciadas por `FUNC`, y finalmente `FIN`; produce `NodoInterface(nombre, metodos)`.

Resultados reales con el programa mínimo:

| Forma | Resultado | Nodo/error |
| --- | --- | --- |
| `interface` | Aceptada | `NodoInterface('I', [NodoMetodoAbstracto('m', [])])` |
| `rasgo` | Aceptada | `NodoInterface('I', [NodoMetodoAbstracto('m', [])])` |
| `trait` | Rechazada como declaración de interfaz | `ParserError: Token inesperado en término: TipoToken.DOSPUNTOS` |
| `interfaz` | Rechazada como declaración de interfaz | `ParserError: Token inesperado en término: TipoToken.DOSPUNTOS` |

Por tanto, `rasgo` no es un alias léxico estéril: llega al mismo despacho, consume el mismo contrato completo y genera el mismo AST que `interface`.

## 4. AST e implementación interna

El nodo resultante es `pcobra.core.ast_nodes.NodoInterface`, cuyos campos son `nombre` y `metodos`; cada firma es un `NodoMetodoAbstracto`. `NodoInterface`, `declaracion_interface` y los métodos `visit_interface` son nombres **E — IMPLEMENTACIÓN INTERNA**, no lexemas fuente. No hay evidencia que aconseje renombrarlos y una reparación superficial no necesita tocarlos.

## 5. `PALABRAS_RESERVADAS`

Sonda exacta de pertenencia sobre el `frozenset` real de 59 entradas:

| Forma | Presente |
| --- | --- |
| `interface` | Sí |
| `rasgo` | No |
| `trait` | No |
| `interfaz` | No |

Existe una divergencia interna: el lexer reconoce tanto `interface` como `rasgo` como keyword, pero la tabla auxiliar sólo reserva `interface`. No se infiere de ello que `rasgo` falle como declaración: la sonda del parser demuestra lo contrario.

## 6. REPL / Pygments

La regla declarada es `(TipoToken.INTERFACE, r"\b(interface|trait)\b", Keyword)`. La sonda real produjo:

| Forma | Token Pygments | Clasificación solicitada |
| --- | --- | --- |
| `interface` | `Token.Keyword` | Keyword |
| `rasgo` | `Token.Name` | Name |
| `trait` | `Token.Keyword` | Keyword |
| `interfaz` | `Token.Name` | Name |

El REPL omite una forma funcional (`rasgo`) y promociona una forma no funcional (`trait`): **B — SUPERFICIE COBRA DIVERGENTE**.

## 7–11. Contrato documental y público

### Libro normativo

`docs/LIBRO_PROGRAMACION_COBRA.md` no documenta la construcción de interfaces/rasgos ni enseña una keyword para ella. Su única coincidencia pertinente por grafía es ``interfaz`` en el índice de `standard_library.interfaz`; es un nombre de módulo, no sintaxis de declaración, y se clasifica **H — APARICIÓN IRRELEVANTE** para este contrato. No aparecen `interface`, `rasgo` ni `trait` como lexemas de esta construcción.

### EBNF

`docs/gramatica.ebnf` no contiene producción ni referencia para `interface`, `rasgo`, `trait` o `interfaz`. La gramática no permite elegir una forma canónica y no debe inventarse una producción en esta auditoría.

### SPEC

`docs/SPEC_COBRA.md` no contiene ninguna de las cuatro grafías ni presenta esta construcción. Por tanto ninguna se define allí como keyword Cobra.

### Guía específica

`docs/interfaces.md` declara expresamente que la keyword Cobra es `interface` y contiene dos ejemplos fuente con `interface Printable:` e `interface Comprimible:`. Ambos son programas compatibles con el parser real. Su única aparición de `trait` está en la frase que enumera las construcciones destino para Python, JavaScript y Rust (`class` abstracta, clase vacía y `trait`); distingue así la fuente Cobra de la salida de backend. Se clasifica `interface` como **C — DOCUMENTACIÓN DE SINTAXIS** y `trait` como **D — BACKEND / CÓDIGO DESTINO**.

### README, tutoriales, ejemplos y documentación pública

`README.md` usa “interfaz” para CLI, GUI o API pública, no para esta construcción. `docs/README.en.md` usa “interface” sólo en prosa sobre la interfaz web. `examples/README.md` referencia el módulo Python `standard_library.interfaz`; `examples/avanzados/README.md` usa el término genérico “interfaz”. No se encontró ejemplo público fuente de `rasgo`; el único ejemplo público de la construcción es el funcional con `interface` en `docs/interfaces.md`. Estas coincidencias incidentales son **H**.

## 12. Tests

| Test/evidencia | Intención solicitada | Resultado contractual |
| --- | --- | --- |
| `tests/test_lexer_parser_contract.py`, mapa de keywords | C — comprobación del lexer | Espera `interface -> INTERFACE` y `rasgo -> INTERFACE`. |
| `tests/test_lexer_parser_contract.py`, lista amplia de palabras | C — comprobación del lexer | Incluye y tokeniza ambas formas; no incluye `trait` ni `interfaz` para esta construcción. |
| `tests/unit/test_interface.py::test_parser_interface` | A — positivo de sintaxis Cobra | Programa completo con `interface Printable:`; valida `NodoInterface` e implementación por clase. |
| `tests/unit/test_interface.py::test_transpiladores_interface_targets_publicos` | A + D | Parsea `interface I:` y comprueba `class I` en Python/JS y `trait I` en Rust. |
| Tests de `standard_library.interfaz` e imports JS `nativos/interfaz.js` | E/F — API interna o incidental | Prueban una biblioteca/runtime, no una keyword fuente. |

No existe test funcional de parser con `rasgo I:` en el corpus; sí existe comprobación positiva del lexer para `rasgo`. Sí existen tests positivos extremo a extremo con `interface`. No hay tests negativos explícitos para `trait` o `interfaz` como declaración.

## 13. Transpilers: semántica y separación fuente/destino

- Python: `visit_interface` emite una `class` con métodos que contienen `pass`.
- JavaScript: `visit_interface` emite una `class` con métodos vacíos.
- Rust: `visit_interface` emite literalmente `trait {nodo.nombre} {`, con firmas `fn ...;`.

El `trait` Rust está verificado además por un test positivo. Es **D — BACKEND / CÓDIGO DESTINO**, correcto y obligatorio de preservar; no demuestra que `trait` sea sintaxis fuente Cobra.

## 14. VS Code / editor

La ruta real es `extensions/vscode/syntaxes/cobra.tmLanguage.json`. Su regex de keywords no contiene `interface`, `rasgo`, `trait` ni `interfaz`, por lo que las cuatro quedan sin alcance `keyword.control.cobra`. `extensions/vscode/snippets/cobra.json` no ofrece snippet de interfaces y ninguna otra coincidencia aparece bajo `extensions/vscode`. Para `interface` y `rasgo`, que sí son fuente funcional, la omisión es **B — SUPERFICIE COBRA DIVERGENTE**; no resaltar `trait` o `interfaz` coincide con el core.

## 15. Historia Git disponible

La historia local tiene 311 commits, pero comienza en un límite injertado (`grafted`): los archivos relevantes aparecen ya completos en el gran snapshot `9b30ac7` (`Fix CodeQL problem query metadata`). En ese snapshot ya coexistían:

- core `interface|rasgo`;
- REPL `interface|trait`;
- documentación y tests funcionales con `interface`;
- tests contractuales del lexer para `interface` y `rasgo`.

`git log -S` no encuentra una introducción separada anterior accesible para `rasgo`, `interface|rasgo`, `interface|trait` o `TipoToken.INTERFACE`: sólo el snapshot. Los commits posteriores sobre “sintaxis española” (`b07d8c9`, `c51326b`, `ae0ceca`, `9c8147e`, `fe2b782`) tratan otros aliases (`with/as`, `in/en`) y no modifican esta construcción. En consecuencia:

- no puede fecharse cuándo se añadió `rasgo`;
- no puede demostrarse que `interface` fuese originalmente la única forma;
- no hay evidencia accesible de que `trait` fuese alias del lexer core;
- no puede atribuirse causalmente la divergencia core/REPL;
- hay evidencia general de campañas posteriores para restaurar sintaxis española, pero no de un commit accesible que españolice específicamente interfaces;
- la presencia inicial de `rasgo` en core y en su test demuestra incorporación deliberada al snapshot contractual, pero la intención histórica exacta no es recuperable.

Esto es **G — EVIDENCIA HISTÓRICA** con una limitación explícita; no se inventa intención.

## Tabla de hallazgos relevantes (20)

| Path | Fragmento | Superficie | Forma | Comportamiento/uso | Clasificación | Acción futura |
| --- | --- | --- | --- | --- | --- | --- |
| `src/pcobra/cobra/core/lexer.py` | `INTERFACE = "INTERFACE"` | Enum | interna | Único token relacionado | E | Conservar nombre interno. |
| `src/pcobra/cobra/core/lexer.py` | `interface\|rasgo` | Lexer core | `interface` | Emite `INTERFACE` | A | Decidir compatibilidad futura. |
| `src/pcobra/cobra/core/lexer.py` | `interface\|rasgo` | Lexer core | `rasgo` | Emite `INTERFACE` | A | Candidata canónica española. |
| `src/pcobra/cobra/core/lexer.py` | fallback identificador | Lexer core | `trait` | Emite `IDENTIFICADOR` | A | Mantener fuera de fuente. |
| `src/pcobra/cobra/core/lexer.py` | fallback identificador | Lexer core | `interfaz` | Emite `IDENTIFICADOR` | A | No añadir sin nueva evidencia. |
| `src/pcobra/cobra/core/parser.py` | despacho `INTERFACE` | Parser | ambas aceptadas | `interface`/`rasgo` llegan al mismo método | A | No requiere duplicar parser. |
| `src/pcobra/cobra/core/parser.py` | `declaracion_interface` | Parser | interna | Consume `INTERFACE`, firma(s), `FIN` | E | Conservar implementación. |
| `src/pcobra/core/ast_nodes.py` | `NodoInterface` | AST | interna | Nodo común para ambas grafías | E | Conservar AST. |
| `src/pcobra/cobra/core/utils.py` | `"interface"` | Reservadas | `interface` | Presente; `rasgo` ausente | B | Alinear según política elegida. |
| `src/pcobra/cobra/cli/repl/cobra_lexer.py` | `interface\|trait` | REPL | `interface` | Keyword correcta respecto al alias actual | A | Revisar al fijar política. |
| `src/pcobra/cobra/cli/repl/cobra_lexer.py` | `interface\|trait` | REPL | `rasgo` | Name aunque core la acepta | B | Resaltar forma canónica. |
| `src/pcobra/cobra/cli/repl/cobra_lexer.py` | `interface\|trait` | REPL | `trait` | Keyword aunque core la rechaza | B | Retirar sólo de sintaxis fuente REPL. |
| `docs/LIBRO_PROGRAMACION_COBRA.md` | módulo `interfaz` | Libro | `interfaz` | Biblioteca, no declaración | H | No usar como evidencia sintáctica. |
| `docs/gramatica.ebnf` / `docs/SPEC_COBRA.md` | ausencia | Norma | todas | Construcción no especificada | I | Documentar tras decisión normativa. |
| `docs/interfaces.md` | `interface Printable:` | Guía pública | `interface` | Enseña fuente funcional | C | Migrar sólo en tarea posterior. |
| `docs/interfaces.md` | ``trait`` destino | Guía backend | `trait` | Equivalente Rust | D | Preservar. |
| `tests/test_lexer_parser_contract.py` | mapa de keywords | Tests | `interface`, `rasgo` | Contrato léxico positivo | F | Añadir cobertura E2E de canónica. |
| `tests/unit/test_interface.py` | programas `interface` | Tests | `interface` | Contrato E2E positivo | F | Resolver compatibilidad antes de cambiar. |
| `src/pcobra/cobra/transpilers/transpiler/to_rust.py` | `trait {nombre}` | Backend | `trait` | Salida Rust legítima | D | No tocar. |
| `extensions/vscode/syntaxes/cobra.tmLanguage.json` | regex sin las cuatro | Editor | todas | No resalta ni siquiera formas funcionales | B | Añadir sólo forma(s) aprobadas. |

## Matriz contractual final

| Forma | Lexer core | Parser | PALABRAS_RESERVADAS | REPL | VS Code | Docs | Tests positivos |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `interface` | `INTERFACE` | Sí, E2E | Sí | Keyword | No keyword | `docs/interfaces.md` la enseña; ausente de Libro/SPEC/EBNF | Sí, lexer y E2E |
| `rasgo` | `INTERFACE` | Sí, E2E (sonda) | No | Name | No keyword | No ejemplo/definición pública | Sí, lexer; no E2E en corpus |
| `trait` | `IDENTIFICADOR` | No como interfaz | No | Keyword | No keyword | Sólo salida Rust en guía específica | Sí sólo como salida Rust; ninguno de fuente |
| `interfaz` | `IDENTIFICADOR` | No como interfaz | No | Name | No keyword | Sólo módulo/prosa incidental | Ninguno de fuente |

## Respuestas explícitas a las 20 preguntas

1. **¿Qué formas tokenizan como `TipoToken.INTERFACE`?** `interface` y `rasgo`.
2. **¿Qué formas llegan realmente a `declaracion_interface()`?** `interface` y `rasgo`, porque ambas producen `INTERFACE`; `trait` e `interfaz` no.
3. **¿`rasgo` es sintaxis funcional completa o sólo alias léxico?** Es sintaxis funcional completa: la sonda E2E produce `NodoInterface` con su método abstracto.
4. **¿`interface` es sintaxis funcional completa?** Sí; lo prueban la sonda y `tests/unit/test_interface.py`.
5. **¿`trait` es sintaxis fuente Cobra funcional?** No. Es `IDENTIFICADOR` y el programa mínimo falla en parser.
6. **¿`interfaz` existe actualmente como sintaxis?** No para esta construcción; es `IDENTIFICADOR`. Sus usos de biblioteca/prosa son ajenos.
7. **¿Qué formas están en `PALABRAS_RESERVADAS`?** Sólo `interface`; no `rasgo`, `trait` ni `interfaz`.
8. **¿Qué formas marca el REPL como keyword?** `interface` y `trait`; marca `rasgo` e `interfaz` como `Name`.
9. **¿Qué formas marca VS Code como keyword?** Ninguna de las cuatro.
10. **¿Qué forma enseñan los documentos principales?** El Libro, SPEC y EBNF no enseñan la construcción. La guía específica pública enseña `interface`; README/tutoriales no añaden otro contrato fuente.
11. **¿Existe un ejemplo público funcional de `rasgo`?** No se encontró. La funcionalidad se verifica por sonda y test léxico, no por ejemplo público versionado.
12. **¿Existe un ejemplo público funcional de `interface`?** Sí, dos en `docs/interfaces.md`.
13. **¿`trait` aparece correctamente como salida Rust?** Sí: `visit_interface` emite `trait Nombre {` y un test lo exige.
14. **¿Hay tests positivos para `rasgo`?** Sí, de contrato léxico; no hay test positivo E2E versionado del parser.
15. **¿Hay tests positivos para `interface`?** Sí, tanto léxicos como E2E y de transpilers.
16. **¿Hay evidencia histórica de intención de españolizar esta construcción?** Evidencia parcial: `rasgo` ya está en core y test al comienzo accesible, y hay campañas generales posteriores de sintaxis española; no existe en la historia disponible un commit específico que explique su introducción.
17. **¿Hay evidencia que justifique conservar `interface` como alias fuente?** Sí para una transición controlada: funciona E2E, es la única forma documentada públicamente y tiene tests E2E. Esa evidencia impide retirarla sin una decisión/migración explícita, aunque no la convierte en canónica española.
18. **¿Qué superficies están claramente desalineadas?** Reservadas omite `rasgo`; REPL omite `rasgo` y añade `trait`; VS Code omite ambas formas funcionales; docs específicas enseñan sólo `interface`; Libro/SPEC/EBNF omiten la construcción; tests E2E cubren sólo `interface`.
19. **¿Puede hacerse una reparación quirúrgica sin cambiar AST/transpilers?** Sí. El único token y nodo ya abstraen ambas grafías; AST, nombres internos y backends pueden permanecer intactos. Cualquier retirada de alias del lexer sí requeriría autorización específica y una decisión de compatibilidad.
20. **¿Qué política futura está mejor respaldada por la evidencia?** En el estado actual, **Política C — transición incompleta**; como destino normativo, investigar **Política A — `rasgo` canónico**, porque es la única forma española ya funcional y probada léxicamente. No hay evidencia para Política B/`interfaz`.

## Política recomendada y propuesta de siguiente Task

### Política mejor respaldada

Adoptar de inmediato la descripción **C (transición incompleta)** y abrir una tarea de decisión/migración cuyo destino propuesto sea **A (`rasgo` canónico)**. Mantener temporalmente `interface` como alias de compatibilidad es lo más prudente hasta medir usuarios y establecer deprecación; no hay base para añadir `interfaz`. `trait` debe quedar reservado al backend Rust, no a la fuente Cobra.

### Task posterior propuesta (no implementada aquí)

1. Declarar `rasgo` como forma fuente canónica.
2. Decidir explícitamente si `interface` se mantiene durante una ventana de compatibilidad/deprecación o se retira; la evidencia actual recomienda transición antes de retirada.
3. Retirar `trait` únicamente de la regex del REPL/Pygments; preservar todas sus emisiones y aserciones como Rust destino.
4. Alinear `src/pcobra/cobra/core/utils.py`, `src/pcobra/cobra/cli/repl/cobra_lexer.py` y `extensions/vscode/syntaxes/cobra.tmLanguage.json` con la decisión.
5. Tras la decisión normativa, actualizar `docs/LIBRO_PROGRAMACION_COBRA.md`, `docs/SPEC_COBRA.md`, `docs/gramatica.ebnf`, `docs/interfaces.md` y referencias públicas pertinentes, sin alterar ejemplos para ocultar fallos.
6. Añadir test E2E positivo de `rasgo I:`; mantener o convertir el test E2E de `interface` según la política de compatibilidad; añadir pruebas de paridad core/REPL/VS Code y rechazo fuente de `trait`/`interfaz` si esa es la decisión final.
7. No tocar `src/pcobra/core/ast_nodes.py`, nombres `NodoInterface`/`visit_interface`/`declaracion_interface`, ni los transpilers Python/JavaScript/Rust.
8. No cambiar la salida `trait` de `src/pcobra/cobra/transpilers/transpiler/to_rust.py` ni su test de backend.
9. No añadir `interfaz`, un token nuevo, aliases nuevos o gramática inventada.

## Control de integridad de esta auditoría

El único archivo creado es `audit_evidence/phase2/task22_interface_rasgo_trait_forensics.md`. Las comprobaciones finales exigidas deben confirmar `git diff --check` limpio y diffs vacíos para `src`, `tests`, `docs` y `extensions`.

CONTRATO INTERFACE/RASGO/TRAIT DIVERGENTE — REPARACIÓN QUIRÚRGICA POSIBLE
