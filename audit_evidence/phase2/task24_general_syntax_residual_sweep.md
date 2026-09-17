# Phase 2 — Task 24: barrido general de divergencias sintácticas residuales

## 1. Alcance, base y método

- **Base obligatoria verificada:** `372cd9b04473e15a90390d4adf264afc1d9de8cc`.
- **Estado inicial:** limpio; `git status --short` no produjo salida.
- **Fecha:** 2026-09-17 (UTC).
- **Naturaleza:** exclusivamente forense. No se modificaron Lexer, Parser, tests,
  documentación normativa, extensiones, ejemplos, dependencias ni configuración.
- **Bloques cerrados:** no se reabrieron `with/as`, `in/en` ni interfaces. Las
  sondas no mostraron una regresión que justificase hacerlo.

Se inspeccionaron `TipoToken`, las expresiones regulares del lexer, el dispatch y
los consumidores del parser, `PALABRAS_RESERVADAS`, el `CobraLexer` real de
Pygments, TextMate, snippets, EBNF, SPEC, Libro, README, documentación secundaria,
tests, ejemplos públicos e historia Git cuando aportaba intención. Además se
ejecutaron sondas de `Lexer(...).tokenizar()`, `ClassicParser(...)` y
`pygments.lex(..., CobraLexer())`.

Las sondas de parser usaron programas mínimos completos. Un resultado `Name` en
Pygments significa que la grafía no fue resaltada como `Keyword`; no significa que
el lexer core la rechazase. Del mismo modo, un nombre español de `TipoToken` no se
interpretó por sí solo como promesa de un lexema español.

## 2. Evidencia transversal

### 2.1 Enum, lexer core y reservadas

El enum contiene los miembros relevantes `FUNC`, `SINO_SI`, `GARANTIA`, `IMPORT`,
`OPCION`, `INTENTAR`, `APLAZAR`, `CAPTURAR`, `LANZAR`, `GENERAR`, `SWITCH`, `CASE`,
`VARIABLE`, `EXPORTAR` y `ENUMERACION`. No contiene `TRY`, `CATCH`, `THROW`,
`DEFER` ni `YIELD`.

Resultado exacto de las sondas léxicas:

| Bloque | Grafía 1 | Grafía 2 | Token core |
| --- | --- | --- | --- |
| try | `try` | `intentar` | ambas `INTENTAR` |
| catch | `catch` | `capturar` | ambas `CAPTURAR` |
| throw | `throw` | `lanzar` | ambas `LANZAR` |
| defer | `defer` | `aplazar` | ambas `APLAZAR` |
| guard | `guard` | `garantia` | ambas `GARANTIA` |
| switch | `switch` | `segun` | ambas `SWITCH` |
| case | `case` | `caso` | ambas `CASE` |
| yield | `yield` | `generar` | `GENERAR` / `IDENTIFICADOR` |
| option | `option` | `opcion` | `OPCION` / `IDENTIFICADOR` |
| import | `import` | `importar` | `IMPORT` / `IDENTIFICADOR` |
| func | `func` | `definir` | ambas `FUNC` |
| elseif | `elseif` | `sino si` | ambas `SINO_SI` |

`PALABRAS_RESERVADAS` coincide con esas salidas salvo una omisión relevante del
bloque obligatorio: `definir` es un `FUNC` funcional, pero no está reservado.
Entre los hallazgos adicionales, `variable` y `exportar` también son tokens core
pero faltan en reservadas; en sentido contrario, `enum` figura como reservada aunque
el lexer la entrega como `IDENTIFICADOR`.

### 2.2 Parser ejecutado

Las combinaciones `try/catch`, `intentar/capturar` y las dos combinaciones mixtas
llegan al mismo `NodoTryCatch`. `throw` y `lanzar` producen `NodoThrow`; `defer f()`
y `aplazar f()` producen `NodoDefer`; `guard` y `garantia` producen
`NodoGarantia`; `switch/case` y `segun/caso` producen `NodoSwitch`; `option`,
`import`, `func`, `definir`, `elseif` y `sino si` alcanzan sus respectivos handlers.

Hay una rotura productiva inequívoca en `yield`: el dispatch selecciona
`declaracion_yield` mediante `TipoToken.GENERAR`, pero el handler intenta consumir
`TipoToken.YIELD`, miembro inexistente. `yield 1` termina en `AttributeError`. En
cambio, `generar 1` no expresa yield: se parsea como un identificador seguido de
otra expresión. La denominación `GENERAR` es, por tanto, interna; no acredita un
alias fuente español.

Para evitar falsos positivos, `opcion`, `importar` y `generar` aislados pueden
parsearse como expresiones de identificador; eso **no** los convierte en las
sentencias `option`, `import` o `yield`. La sonda de la forma estructural confirma
que no activan sus handlers.

### 2.3 Herramientas

- **REPL/Pygments:** ambas grafías son `Keyword` para try, catch, throw, switch,
  case y func. `yield`, `option` e `import` son `Keyword`, y sus supuestas
  traducciones son `Name`. Las dos grafías de defer y guard son `Name`; `elseif`
  es `Name`, aunque `sino si` queda dividido en dos `Keyword`. `exportar` también
  es `Name`.
- **VS Code/TextMate:** cubre las parejas try/catch/throw, switch/case y func;
  cubre `yield` e `import`. Omite por completo defer, guard, option, elseif,
  exportar y enumeracion. `sino si` se colorea por coincidencias separadas de
  `sino` y `si`, no como la alternativa compuesta declarada por core.
- **Snippets:** sólo existen plantillas para `func`, `si/sino` y `para`; no
  presentan aliases contradictorios para los candidatos restantes.

### 2.4 Documentación y tests

El Libro es la fuente normativa. Su índice autogenerado enumera try/catch/throw y
sus formas españolas, guard/garantia, switch/case, `elseif`/`sino si`, `yield`,
`import` y `func`; la sección de errores enseña como forma principal
`intentar`/`capturar`/`lanzar`. También declara explícitamente en su tabla de reglas
pedagógicas que las funciones se declaran con `func` o `definir`.

Sin embargo, el Libro no incluye `defer` ni `aplazar`; tampoco incluye `segun` ni
`caso`, pese a que core los acepta. `exportar` tampoco está en el contrato del
Libro. El Manual secundario sí anuncia `defer`/`aplazar`, por lo que no basta la
evidencia técnica para escoger política normativa en ese bloque.

La EBNF documenta las parejas try/catch y guard, pero sólo `switch`, `case`,
`option`, `import` y `func`; omite throw/lanzar, defer/aplazar, yield y la cascada
`elseif`/`sino si`. La SPEC incluye las parejas de excepciones, guard y cascada,
pero mantiene switch/case sólo en inglés. Un ejemplo aislado de SPEC usa
`importar utilidades`, contradiciendo su propia gramática y el contrato normativo;
se considera un ejemplo obsoleto, no un alias implementado.

`tests/test_lexer_parser_contract.py` prueba positivamente la tokenización de las
grafías core anteriores, pero no prueba el parseo de cada alias. Existen tests de
parser positivos para try/catch en inglés y español, defer/aplazar, garantia,
switch/case, enumeracion y las cascadas condicionales. Para yield, las pruebas
construyen `NodoYield` directamente en intérprete/transpilers: no hay una regresión
positiva Lexer→Parser que detecte el `TipoToken.YIELD` inexistente. Para `guard`,
`segun` y `caso`, la cobertura positiva observada es principalmente léxica; los
tests estructurales usan las formas `garantia`, `switch` y `case`.

### 2.5 Historia útil

Task 7 y su reparación establecieron el modelo correcto para excepciones:
aliases textuales ingleses y españoles convergen en tokens internos españoles; no
deben inventarse miembros `TRY`, `CATCH` o `THROW`. Task 8/9 aplicó el mismo modelo
a defer/aplazar y corrigió el consumo `DEFER` a `APLAZAR`; el estado actual prueba
que ambas grafías funcionan.

`git blame` atribuye tanto el lexer `yield -> GENERAR` como el consumo inválido
`TipoToken.YIELD` al límite histórico disponible (`0e78ef2`, commit grafted). La
historia disponible no demuestra una migración posterior ni una intención de
aceptar `generar`; sí demuestra que la contradicción parser/enum no es causada por
los cierres recientes de Phase 2.

## 3. Análisis y clasificación por candidato

### A. `try / intentar`

Ambas grafías se normalizan a `INTENTAR`, entran al mismo handler y funcionan con
cualquiera de las dos capturas. Reservadas, REPL y TextMate coinciden. Libro,
EBNF y SPEC reconocen ambas; hay pruebas positivas en inglés y español. La forma
pedagógica principal del Libro es `intentar`, mientras `try` permanece como alias
funcional documentado. **Clasificación B — COMPATIBILIDAD BILINGÜE COHERENTE.**

### B. `catch / capturar`

Ambas se normalizan a `CAPTURAR`; no existen ni hacen falta miembros separados.
Core, herramientas, reservadas y documentación coinciden, y las combinaciones
mixtas parsean. **Clasificación B — COMPATIBILIDAD BILINGÜE COHERENTE.**

### C. `throw / lanzar`

Ambas producen `LANZAR` y `NodoThrow`; reservadas, REPL, TextMate, Libro y SPEC
coinciden. La EBNF no contiene la sentencia, pese a que su `statement` tampoco la
enumera. Es una omisión documental concreta, no un defecto del alias.
**Clasificación D — DOCUMENTACIÓN OBSOLETA.**

### D. `defer / aplazar`

Ambas formas son funcionales, reservadas y probadas; Task 9 dejó el parser alineado
con `APLAZAR`. REPL y TextMate no resaltan ninguna. El Manual presenta ambas, pero
EBNF, SPEC y el Libro normativo no presentan la construcción. Antes de sincronizar
herramientas debe decidirse si es sintaxis pública y si ambas grafías permanecen.
**Clasificación I — REQUIERE DECISIÓN NORMATIVA.**

### E. `guard / garantia`

Ambas formas producen `GARANTIA` y parsean. Están reservadas y documentadas como
pareja en Libro/EBNF/SPEC, pero las dos son `Name` en REPL y faltan en TextMate.
**Clasificación C — DIVERGENCIA DE HERRAMIENTAS.**

### F. `switch / segun`

Ambas formas producen `SWITCH`, parsean y están reservadas/resaltadas. EBNF, SPEC
y Libro sólo enseñan `switch`; no se halló prueba estructural positiva de `segun`.
La keyword española funcional carece de respaldo normativo visible.
**Clasificación D — DOCUMENTACIÓN OBSOLETA.**

### G. `case / caso`

Ambas formas producen `CASE`, parsean y están reservadas/resaltadas. Igual que en
switch, EBNF, SPEC y Libro sólo enseñan `case`, y la prueba estructural usa la forma
inglesa. **Clasificación D — DOCUMENTACIÓN OBSOLETA.**

### H. `yield / generar`

Sólo `yield` es lexema. `GENERAR` es el nombre interno del token; `generar` sigue
siendo identificador y no está reservado ni resaltado. `yield` está documentado y
resaltado, pero no puede atravesar el parser porque éste consume el inexistente
`TipoToken.YIELD`. AST, intérprete y transpilers sí tienen soporte construido a
mano. **Clasificación G — IMPLEMENTACIÓN PARCIAL.**

### I. `option / opcion`

Sólo `option` activa `OPCION`; `opcion` es un identificador. EBNF, SPEC y pruebas
léxicas respaldan la forma inglesa, y REPL coincide. TextMate omite `option`. No
hay evidencia de que `opcion` sea alias prometido. **Clasificación C — DIVERGENCIA
DE HERRAMIENTAS.**

### J. `import / importar`

Sólo `import` activa `IMPORT`; `importar` es identificador. Libro, EBNF, gramática
de SPEC, README, reservadas, REPL y TextMate respaldan `import`. El uso aislado de
`importar utilidades` en SPEC contradice ese conjunto y no prueba un alias.
**Clasificación A — COHERENTE Y DELIBERADO** (con un ejemplo secundario obsoleto
que debe tratarse separadamente, no cambiando core).

### K. `func / definir`

Ambas formas producen `FUNC`, parsean y son `Keyword` en REPL/TextMate. El Libro
declara expresamente ambas formas, pero EBNF/SPEC sólo incluyen `func` y
`PALABRAS_RESERVADAS` omite `definir`. La compatibilidad funcional es clara; las
superficies auxiliares no están sincronizadas. **Clasificación C — DIVERGENCIA DE
HERRAMIENTAS.**

### L. `elseif / sino si`

El lexer normaliza ambas formas a un único `SINO_SI` antes de que el patrón `SINO`
pueda capturar el prefijo; el parser consume ese token y ambas cascadas funcionan.
Reservadas y SPEC incluyen ambas. EBNF omite la cascada; REPL marca `elseif` como
`Name` y divide `sino si`; TextMate omite `elseif` y sólo colorea los dos términos
por separado. **Clasificación C — DIVERGENCIA DE HERRAMIENTAS.**

### M. Descubrimiento: `variable` y `:=`

`variable` produce `VARIABLE`; el parser lo interpreta como declaración por
inferencia y exige `:=`, mientras EBNF/SPEC prometen `variable IDENTIFICADOR =
expr`. Además falta en `PALABRAS_RESERVADAS`, aunque REPL/TextMate sí lo resaltan.
`variable x := 1` funciona y `variable x = 1` falla. **Clasificación G —
IMPLEMENTACIÓN PARCIAL.**

### N. Descubrimiento: `exportar`

`exportar x` produce `EXPORTAR`, llega a `NodoExport` y tiene cobertura léxica,
pero falta en reservadas, REPL, TextMate, EBNF, SPEC y Libro. Es implementación
accesible desde fuente sin una superficie pública completa. **Clasificación G —
IMPLEMENTACIÓN PARCIAL.**

### O. Descubrimiento: `enum / enumeracion`

`enumeracion` produce `ENUMERACION` y parsea; `enum` produce `IDENTIFICADOR` y no
activa la declaración. Pese a ello, `enum` está en `PALABRAS_RESERVADAS`, Libro y
SPEC prometen ambas formas, y un test incluso espera advertencias por mezclar los
dos aliases. REPL sólo resalta `enumeracion`; TextMate no resalta ninguna.
**Clasificación F — ALIAS FANTASMA.**

## 4. Tabla resumen obligatoria

| Candidato | Core | Parser | Reservadas | REPL | VS Code | Docs | Tests | Clasificación | Riesgo | Acción |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `try/intentar` | ambas→INTENTAR | ambas OK | ambas | ambas Keyword | ambas | ambas | positivas ambas | B | BAJO | ninguna |
| `catch/capturar` | ambas→CAPTURAR | ambas OK | ambas | ambas Keyword | ambas | ambas | positivas ambas | B | BAJO | ninguna |
| `throw/lanzar` | ambas→LANZAR | ambas OK | ambas | ambas Keyword | ambas | EBNF omite | positivas | D | BAJO | EBNF separada |
| `defer/aplazar` | ambas→APLAZAR | ambas OK | ambas | ambas Name | ninguna | Libro/EBNF omiten | positivas ambas | I | ALTO | decidir política |
| `guard/garantia` | ambas→GARANTIA | ambas OK | ambas | ambas Name | ninguna | ambas | parser sólo garantia | C | BAJO | alinear resaltado |
| `switch/segun` | ambas→SWITCH | ambas OK | ambas | ambas Keyword | ambas | sólo switch | lexer ambas | D | MEDIO | aclarar docs |
| `case/caso` | ambas→CASE | ambas OK | ambas | ambas Keyword | ambas | sólo case | lexer ambas | D | MEDIO | aclarar docs |
| `yield/generar` | yield→GENERAR; generar→ID | yield roto | sólo yield | Keyword/Name | sólo yield | sólo yield | AST, no parser | G | BAJO | reparar consumo |
| `option/opcion` | option→OPCION; opcion→ID | option OK | sólo option | Keyword/Name | ninguna | sólo option | lexer | C | BAJO | TextMate |
| `import/importar` | import→IMPORT; importar→ID | import OK | sólo import | Keyword/Name | sólo import | import; ejemplo SPEC errado | positivas import | A | BAJO | ninguna de core |
| `func/definir` | ambas→FUNC | ambas OK | falta definir | ambas Keyword | ambas | Libro ambas; gramáticas sólo func | lexer ambas | C | BAJO | reservadas/docs |
| `elseif/sino si` | ambas→SINO_SI | ambas OK | ambas | Name / 2 Keyword | sólo palabras separadas | SPEC ambas; EBNF omite | parser ambas | C | BAJO | alinear resaltado |
| `variable/:=` | variable→VARIABLE | sólo `:=` | falta variable | Keyword | sí | gramáticas prometen `=` | lexer | G | ALTO | forense propio |
| `exportar` | EXPORTAR | OK | falta | Name | falta | ausente | sólo lexer | G | ALTO | decisión de superficie |
| `enum/enumeracion` | ID / ENUMERACION | sólo enumeracion | ambas | Name/Keyword | ninguna | promete ambas | expectativa alias | F | MEDIO | forense propio |

## 5. Matriz de prioridad

El alcance estima los archivos de una futura tarea correctamente acotada, no los
archivos modificados por este informe.

| Candidato | Confianza | Riesgo de cambio | Alcance estimado |
| --- | --- | --- | --- |
| `try/intentar` | ALTA | BAJO | 1–2 archivos |
| `catch/capturar` | ALTA | BAJO | 1–2 archivos |
| `throw/lanzar` | ALTA | BAJO | 1–2 archivos |
| `defer/aplazar` | MEDIA | ALTO | > 5 archivos |
| `guard/garantia` | ALTA | BAJO | 1–2 archivos |
| `switch/segun` | MEDIA | MEDIO | 3–5 archivos |
| `case/caso` | MEDIA | MEDIO | 3–5 archivos |
| `yield/generar` | ALTA | BAJO | 1–2 archivos |
| `option/opcion` | ALTA | BAJO | 1–2 archivos |
| `import/importar` | ALTA | BAJO | 1–2 archivos |
| `func/definir` | ALTA | BAJO | 3–5 archivos |
| `elseif/sino si` | ALTA | BAJO | 3–5 archivos |
| `variable/:=` | ALTA | ALTO | 3–5 archivos |
| `exportar` | ALTA | ALTO | > 5 archivos |
| `enum/enumeracion` | ALTA | MEDIO | 3–5 archivos |

Los bloques coherentes no requieren realmente cambio; su alcance sólo expresa el
tamaño máximo de una comprobación/regresión focal si se volviesen a auditar.

## 6. Respuestas a las 15 preguntas

1. **¿Cuántos bloques sintácticos se auditaron?** Quince: los doce obligatorios y
   tres descubrimientos (`variable/:=`, `exportar`, `enum/enumeracion`).
2. **¿Cuántos están coherentes?** Tres: try/intentar, catch/capturar e
   import/importar (en este último, `importar` no es alias y no debe inferirse).
3. **¿Cuántos tienen divergencia real?** Once. Incluyen desalineaciones de
   herramienta/documentación y tres implementaciones parciales, además del alias
   fantasma. Se cuentan separadamente del bloque normativo ambiguo.
4. **¿Cuántos requieren decisión normativa?** Uno: defer/aplazar.
5. **¿Hay aliases fantasma?** Sí: `enum` está reservado y documentado como alias,
   pero el lexer core lo trata como identificador y el parser no entra a enum.
6. **¿Hay keywords españolas funcionales sin documentación?** Sí: `segun` y
   `caso` no aparecen como sintaxis en Libro/EBNF/SPEC; `aplazar` falta en el Libro
   normativo; `exportar` funciona pero falta en las superficies normativas.
7. **¿Hay keywords inglesas funcionales sin equivalente español?** Sí: `yield`,
   `option` e `import`. `generar`, `opcion` e `importar` son identificadores, no
   aliases. Esto no implica por sí solo un defecto.
8. **¿Hay divergencias core/REPL?** Sí: defer/aplazar, guard/garantia, `elseif` y
   `exportar` funcionan en core pero son `Name` en Pygments.
9. **¿Hay divergencias core/VS Code?** Sí: TextMate omite defer/aplazar,
   guard/garantia, option, elseif, exportar y enumeracion; para `sino si` sólo
   coincide accidentalmente por las dos keywords simples.
10. **¿Hay divergencias core/PALABRAS_RESERVADAS?** Sí: faltan `definir`,
    `variable` y `exportar`; sobra `enum` respecto del reconocimiento core.
11. **¿Qué candidato tiene mayor confianza y menor riesgo?** `yield/generar`: el
    fallo es reproducible, la causa es una referencia única a un miembro
    inexistente y la política léxica (`yield` único lexema, `GENERAR` token interno)
    es inequívoca.
12. **¿Cuál debe ser la siguiente microtarea?** Reparar exclusivamente el consumo
    del token de yield y añadir una regresión Lexer→Parser, sin añadir `generar`.
13. **¿Qué archivos afectaría esa microtarea?** Probablemente
    `src/pcobra/cobra/core/parser.py` y un único archivo focal de tests (preferible
    `tests/unit/test_decoradores_yield.py` o un test de parser dedicado).
14. **¿Qué archivos NO deberían tocarse?** Lexer, `PALABRAS_RESERVADAS`, AST,
    intérprete, transpilers, REPL, TextMate, snippets, docs, README, ejemplos,
    dependencias, workflows y auditorías previas.
15. **¿La siguiente tarea debe ser forense o de reparación directa?**
    **REPARACIÓN DIRECTA**, pero sólo con autorización explícita para tocar Parser,
    como exige `AGENTS.md`; sin esa autorización el hallazgo queda bloqueado y no
    debe improvisarse una corrección en otra capa.

## 7. Conclusión priorizada

El barrido no avala una eliminación general de palabras inglesas. Try/catch son
compatibilidad bilingüe coherente; `import`, `option` y `yield` muestran que un
lexema inglés puede ser el único contrato fuente; `GENERAR` demuestra que un enum
español puede ser sólo representación interna. Por otro lado, defer requiere una
decisión normativa antes de sincronizar herramientas, y enum constituye el único
alias fantasma identificado.

La rotura de yield tiene precedencia porque es independiente, reproducible, no
requiere decidir aliases y puede resolverse de manera quirúrgica. Esta Task 24 no
la implementa.

## SIGUIENTE MICROTAREA RECOMENDADA

```text
Candidato: yield / generar
Clasificación: G — IMPLEMENTACIÓN PARCIAL
Confianza: ALTA
Riesgo: BAJO
Motivo: `yield` se normaliza correctamente a `TipoToken.GENERAR`, pero el handler alcanzable consume el miembro inexistente `TipoToken.YIELD`; `generar` es sólo un identificador y no debe añadirse como alias. Es una contradicción única, ejecutable y análoga a los cierres de tokens canónicos de Tasks 7 y 9.
Archivos probablemente afectados: src/pcobra/cobra/core/parser.py y un único test focal Lexer→Parser (preferentemente tests/unit/test_decoradores_yield.py o un archivo de parser dedicado).
Archivos prohibidos: src/pcobra/cobra/core/lexer.py, src/pcobra/cobra/core/utils.py, AST, runtime/intérprete, transpilers, REPL/Pygments, extensions/, docs/, README.md, ejemplos, dependencias, workflows y auditorías previas.
Tipo de tarea siguiente: REPARACIÓN DIRECTA
```
