# TASK 34 — Auditoría forense de `enum` / `enumeracion`

## Estado base

- Repositorio: `Alphonsus411/pCobra`.
- Rama de trabajo observada: `work`.
- SHA solicitado y efectivamente auditado antes de crear este informe:
  `990e28d7d6ba668ffc2eb49cee1b8c79b2cb0bf4`.
- Alcance: observación del core, superficies auxiliares, pruebas y la historia Git
  disponible. No se cambió comportamiento ni ningún archivo preexistente.

## Conclusión ejecutiva

En el SHA base, **la única sintaxis fuente funcional es `enumeracion`**.
`enum` se tokeniza como identificador, no alcanza `declaracion_enum` y una
declaración completa falla. No hay evidencia en la historia disponible de que
`enum` se haya tokenizado nunca como `ENUMERACION`, por lo que no es un alias
histórico que se haya roto durante una refactorización.

Sin embargo, tampoco es una mera mención documental aislada: desde el primer
snapshot disponible del core aparecen simultáneamente la afirmación explícita
de la SPEC de que ambas formas son sinónimas, `enum` en reservadas, una
infraestructura de seguimiento de aliases y una prueba positiva que intenta
mezclar `enum` con `enumeracion`. Esa prueba falla. La evidencia demuestra una
intención contractual coherente pero una implementación incompleta desde su
introducción. Por ello la clasificación final es **E — Implementación parcial**.

## Matriz de superficies

| Superficie | `enumeracion` | `enum` | Evidencia |
| --- | --- | --- | --- |
| `TipoToken` | Representada por `TipoToken.ENUMERACION`, cuyo nombre y valor son exactamente `"ENUMERACION"`. | No tiene miembro propio; sólo podría compartir `ENUMERACION`, pero no hay regla que lo haga. | `src/pcobra/cobra/core/lexer.py:17-25`. |
| Lexer core | `r"\benumeracion\b"` produce `Token(TipoToken.ENUMERACION, "enumeracion", 1, 1)`. | No existe regex; cae en identificador y produce `Token(TipoToken.IDENTIFICADOR, "enum", 1, 1)`. | Regla en `lexer.py:218`; sondas reproducidas abajo. |
| Parser | `_factories[TipoToken.ENUMERACION]` llama a `declaracion_enum`; produce `NodoEnum`. | No hay dispatch ni rama textual `"enum"`; comienza como expresión identificadora y la declaración completa falla al llegar a `:`. | `parser.py:86-95, 142, 310-379, 1380-1409`. |
| `PALABRAS_RESERVADAS` | Sí. Además, ya llega como token estructural, pero en posición de nombre la asignación consulta su valor antes de validar el tipo. | Sí. Aunque léxicamente es identificador, la validación de nombres impide usarlo como variable. | `utils.py:33-97`; `parser.py:463-501`; sondas. |
| REPL / Pygments | Dos reglas idénticas consecutivas la clasifican como `Keyword`. La segunda es inalcanzable/redundante y no cambia el resultado. | Sin regla: la regla general de identificador la clasifica como `Name`. | `src/pcobra/cobra/cli/repl/cobra_lexer.py:51-52` y regla de identificador posterior. |
| VS Code | No reconocida como keyword. | No reconocida como keyword. | Búsqueda sin coincidencias en `extensions/vscode/syntaxes/cobra.tmLanguage.json`. |
| EBNF | No hay literal, producción de enum ni inclusión en `statement`. | Igual. | `docs/gramatica.ebnf`: `statement` enumera sus alternativas sin enum y no hay coincidencias textuales. |
| SPEC | Aparece en inventario de keywords y en afirmación manual explícita de sinonimia. No hay producción ni ejemplo de declaración enum. | Igual; afirma que ambas se aceptan y que mezclar aliases genera advertencia, lo cual no coincide con el core. | `docs/SPEC_COBRA.md:76,145-148`. |
| Libro | Sólo aparece en el índice de palabras reservadas autogenerado. | Sólo aparece en ese índice autogenerado. | `docs/LIBRO_PROGRAMACION_COBRA.md:80,89,128-129`; no hay ejemplo, explicación pedagógica ni afirmación manual. |
| README | Sin apariciones. | Sin apariciones. | Búsqueda exacta e insensible a mayúsculas en `README.md` y `docs/README.en.md`. |
| Tests | Cobertura positiva Lexer → Parser en `test_enum.py` y `test_parser.py`; contrato léxico explícito. | No hay prueba léxica positiva. Sí hay una prueba de parser que pretende usarlo como alias y falla, y una prueba que sólo comprueba que no sea nombre de variable. | `tests/unit/test_enum.py:12-25`; `tests/unit/test_parser.py:90-113`; `tests/unit/test_reserved_identifiers.py:67-73`; `tests/test_lexer_parser_contract.py:78,219`. |
| Python backend | Soporta `NodoEnum` y tiene prueba construyendo el AST directamente; también puede recibirlo desde fuente `enumeracion`. | El visitante AST no demuestra soporte de esta grafía fuente. | `python_nodes/enum.py`; `tests/unit/test_enum.py:29-34`. |
| JS backend | Soporta `NodoEnum` y tiene prueba construyendo el AST directamente; también puede recibirlo desde fuente `enumeracion`. | El visitante AST no demuestra soporte de esta grafía fuente. | `js_nodes/enum.py`; `tests/unit/test_enum.py:36-41`. |
| Rust backend | No soporta `NodoEnum`: la sonda directa lanza `NotImplementedError('No se ha implementado visit_NodoEnum')`; no hay prueba enum Rust. | Tampoco, y ello es independiente de la grafía fuente. | `to_rust.py` no registra `visit_enum`; sonda reproducida abajo. |

## Lexer core

`TipoToken` declara un único miembro relevante, `ENUMERACION =
"ENUMERACION"`. La lista ordenada de especificaciones contiene exactamente
`(TipoToken.ENUMERACION, re.compile(r"\benumeracion\b"))`. No existe un patrón
`enum`, ni un patrón alternativo `(enum|enumeracion)`.

Los valores exactos observados fueron:

- `enumeracion`: tipo Python `TipoToken`, miembro
  `TipoToken.ENUMERACION`, `tipo.name == "ENUMERACION"`,
  `tipo.value == "ENUMERACION"`, valor Python `str` igual a
  `"enumeracion"`, línea 1, columna 1.
- `enum`: tipo Python `TipoToken`, miembro `TipoToken.IDENTIFICADOR`,
  `tipo.name == tipo.value == "IDENTIFICADOR"`, valor Python `str` igual a
  `"enum"`, línea 1, columna 1.

En ambos casos `analizar_token()` añade después `Token(TipoToken.EOF, None,
1, 12)` y `Token(TipoToken.EOF, None, 1, 5)`, respectivamente.

## Parser

`ALIAS_DECLARACION_ENUM` contiene **sólo** `TipoToken.ENUMERACION` y
`TOKEN_A_LEXEMA` sólo lo proyecta a `"enumeracion"`. El despacho se basa en el
tipo del token: `_factories` asocia `TipoToken.ENUMERACION` con
`declaracion_enum`. No existe una rama `token.valor == "enum"`; la única rama
textual comparable en `declaracion()` es la compatibilidad de `definir`.

`declaracion_enum` consume el tipo permitido, exige nombre identificador y
`:`, acumula identificadores separados opcionalmente por comas hasta `fin`, y
devuelve `NodoEnum(nombre, miembros)`. Por eso `enumeracion Color: ROJO, VERDE
fin` produce un nodo con `nombre == "Color"` y `miembros == ["ROJO",
"VERDE"]`.

`enum Color: ...` no llega accidentalmente al handler: `enum` se interpreta
como el comienzo de una expresión `NodoIdentificador`; el siguiente
identificador queda para otra declaración y finalmente `:` entra en
`termino()`, que lanza `ParserError('Token inesperado en término:
TipoToken.DOSPUNTOS')`. Incluso `enum` aislado es aceptado como una expresión
identificadora, una consecuencia distinta de ser válido como nombre declarado.

La maquinaria `_consumir_alias_palabra_clave` registra los valores textuales
de tokens ya reconocidos. Podría distinguir dos grafías que compartiesen tipo,
pero hoy sólo puede recibir `enumeracion`; por eso la advertencia prometida al
mezclar aliases es inalcanzable para `enum`.

## Palabras reservadas y asignaciones

`PALABRAS_RESERVADAS` contiene tanto `"enum"` como `"enumeracion"`. En
`declaracion_asignacion`, después de consumir `var`, el parser toma el token
actual y consulta **su valor** en el conjunto antes de exigir que su tipo sea
`IDENTIFICADOR`. Esto explica las dos rutas:

- `var enum = 1`: el lexer entrega `enum` como `IDENTIFICADOR`, pero la consulta
  por valor lanza `ParserError("El identificador 'enum' es una palabra
  reservada")`.
- `var enumeracion = 1`: el lexer entrega `enumeracion` como `ENUMERACION`; aun
  así, la consulta por valor ocurre antes de la comprobación de tipo y lanza el
  mismo error adaptado a `enumeracion`, en vez de `Se esperaba un
  identificador...`.

Por tanto, reservar `enum` sí tiene un efecto práctico (prohíbe ese nombre),
pero **no** lo convierte en keyword léxica ni en declaración enum.

## REPL, VS Code y gramática pública

El lexer Pygments contiene dos entradas consecutivas idénticas para
`enumeracion`. Al ser equivalentes y estar antes de la regla general de nombres,
la primera consume la palabra; la duplicación no altera el resultado observable.
No hay entrada `enum`, que termina como `Token.Name`.

El TextMate de VS Code no contiene ninguna de las dos cadenas. La EBNF tampoco:
no declara una producción de enumeración y `statement` no incluye tal
construcción. Así, la gramática pública formal no define enums, aunque el parser
sí implemente la forma española.

## SPEC, Libro y README

La SPEC hace dos tipos de aparición:

1. inventario de keywords `enum`/`enumeracion`;
2. texto explícito que afirma que las enumeraciones aceptan ambas formas, las
   llama sinónimos y promete advertencia al mezclarlas.

No aporta producción formal ni ejemplo enum. La afirmación explícita contradice
el core actual y su propia EBNF mostrada al inicio del documento.

En el Libro, ambas palabras están sólo entre `<!-- BEGIN:
AUTO-SYNTAX-INDEX -->` y su cierre, en la subsección “Palabras reservadas
(gramática + SPEC)”. No se hallaron fuera de ese bloque: no hay texto normativo
manual, ejemplo pedagógico ni afirmación explícita sobre su equivalencia. Dado
que el índice agrega gramática y SPEC, su presencia no es evidencia normativa
independiente.

Ni el README español ni el inglés contienen ninguna aparición, por lo que no
hay allí sintaxis fuente, explicación técnica, nombre interno, alias declarado
ni inventario que clasificar.

## Tests y backends

- `tests/unit/test_enum.py` prueba dos fuentes `enumeracion` de extremo a
  extremo y después prueba Python y JavaScript construyendo `NodoEnum`
  directamente. Estas dos últimas pruebas son cobertura AST → backend, no
  evidencia léxica para `enum`.
- `tests/unit/test_parser.py::test_parser_declaracion_enumeracion` cubre la forma
  española. `test_parser_advertencia_alias_enum` es una prueba positiva real de
  la intención de alias: su fuente mezcla `enum` y `enumeracion` y espera una
  advertencia con ambas grafías. En el estado base falla antes de esa aserción.
- `tests/unit/test_reserved_identifiers.py` presupone que ambas grafías están
  reservadas, no que ambas declaren enums; los dos parámetros pasan.
- `tests/test_lexer_parser_contract.py` incluye sólo `enumeracion` en el mapa y
  conjunto de cobertura léxica. La ausencia de `enum` es consistente con el
  lexer real pero contradice la prueba de alias del parser.
- Python y JavaScript registran visitantes para `NodoEnum`. Rust no tiene módulo
  enum, registro de visitante ni prueba equivalente; un AST directo falla con
  `NotImplementedError`.

## Sondas ejecutadas

### Script reproducible

Desde la raíz, con el entorno del repositorio:

```bash
python - <<'PY'
from pcobra.cobra.core.lexer import Lexer
from pcobra.cobra.core import Parser

for code in (
    "enumeracion", "enum",
    "enumeracion Color: ROJO, VERDE fin",
    "enum Color: ROJO, VERDE fin",
    "var enum = 1", "var enumeracion = 1",
):
    print("SOURCE", repr(code))
    tokens = Lexer(code).analizar_token()
    print("TOKENS", repr(tokens))
    print("TYPES", [(t.tipo.name, t.tipo.value, t.valor,
                     type(t.valor).__name__) for t in tokens])
    try:
        parser = Parser(tokens)
        ast = parser.parsear()
        print("AST", [(type(n).__name__, vars(n)) for n in ast])
        print("WARNINGS", parser.advertencias)
    except Exception as exc:
        print("PARSE_ERROR", type(exc).__name__, repr(str(exc)))
PY
```

### Resultados exactos relevantes

| Fuente | Tokens (sin abreviar tipos) | Resultado parser |
| --- | --- | --- |
| `enumeracion` | `ENUMERACION('enumeracion') @ 1:1`, `EOF(None) @ 1:12` | `ParserError('Se esperaba un nombre de enum')` |
| `enum` | `IDENTIFICADOR('enum') @ 1:1`, `EOF(None) @ 1:5` | `[NodoIdentificador]`, `{'nombre': 'enum', 'valor': 'enum'}` |
| `enumeracion Color: ROJO, VERDE fin` | `ENUMERACION('enumeracion')`, `IDENTIFICADOR('Color')`, `DOSPUNTOS(':')`, `IDENTIFICADOR('ROJO')`, `COMA(',')`, `IDENTIFICADOR('VERDE')`, `FIN('fin')`, `EOF(None)` | `[NodoEnum]`, `{'nombre': 'Color', 'miembros': ['ROJO', 'VERDE']}`; sin advertencias |
| `enum Color: ROJO, VERDE fin` | `IDENTIFICADOR('enum')`, `IDENTIFICADOR('Color')`, `DOSPUNTOS(':')`, `IDENTIFICADOR('ROJO')`, `COMA(',')`, `IDENTIFICADOR('VERDE')`, `FIN('fin')`, `EOF(None)` | `ParserError('Token inesperado en término: TipoToken.DOSPUNTOS')` |
| `var enum = 1` | `VAR('var')`, `IDENTIFICADOR('enum')`, `ASIGNAR('=')`, `ENTERO(1)`, `EOF(None)` | `ParserError("El identificador 'enum' es una palabra reservada")` |
| `var enumeracion = 1` | `VAR('var')`, `ENUMERACION('enumeracion')`, `ASIGNAR('=')`, `ENTERO(1)`, `EOF(None)` | `ParserError("El identificador 'enumeracion' es una palabra reservada")` |

Las posiciones completas de las declaraciones fueron, respectivamente,
`1:1, 1:13, 1:18, 1:20, 1:24, 1:26, 1:32, 1:35` y
`1:1, 1:6, 1:11, 1:13, 1:17, 1:19, 1:25, 1:28`.

Una sonda Pygments con `pygments.lex(..., CobraLexer())` produjo
`Token.Keyword` para `enumeracion` y `Token.Name` para `enum` (además del salto
de línea `Token.Text.Whitespace` que Pygments agrega). Una sonda directa de
`TranspiladorRust().generate_code([NodoEnum(...)])` produjo exactamente
`NotImplementedError('No se ha implementado visit_NodoEnum')`.

## Pruebas ejecutadas

| Comando | Resultado en el SHA base |
| --- | --- |
| `pytest -q tests/unit/test_enum.py` | **4 passed** en 0.90 s. |
| `pytest -q tests/unit/test_parser.py -k enumeracion` | **1 passed, 3 deselected** en 0.26 s. |
| `pytest -q tests/unit/test_reserved_identifiers.py -k enum` | **2 passed, 10 deselected** en 0.24 s. |
| `pytest -q tests/test_lexer_parser_contract.py` | **5 passed** en 0.15 s. |
| `pytest -q tests/unit/test_parser.py::test_parser_advertencia_alias_enum` | **1 failed** en 0.56 s: `ParserError: Token inesperado en término: TipoToken.DOSPUNTOS`. |

El fallo adicional es directamente pertinente y confirma una contradicción
legacy ya presente; no se modificó la prueba. Estos comandos son pruebas
dirigidas, no una ejecución de CI global, y este informe no afirma que la CI
global esté verde.

## Historia Git

### Evidencia disponible

- `git blame` atribuye el miembro `ENUMERACION`, la regex exclusiva
  `\benumeracion\b`, `ALIAS_DECLARACION_ENUM`, ambas reservadas, el parser enum
  y la afirmación de la SPEC al mismo commit
  `1981904a970141f9e8c77c43b71c04383a619c66` (merge PR #3335, 2026-07-19).
- Ese commit es el primer commit que añade las rutas actuales
  `src/pcobra/cobra/core/lexer.py`, `parser.py`, `utils.py` y
  `docs/SPEC_COBRA.md`. En su snapshot inicial ya existe la contradicción:
  lexer sólo español, pero reservadas y SPEC con ambas formas.
- Los snapshots disponibles del lexer en `1981904a`, `ae0ceca6` y `9c8147e1`
  contienen siempre exactamente
  `TipoToken.ENUMERACION, re.compile(r"\benumeracion\b")`; ninguno contiene
  una alternativa `enum`.
- `ALIAS_DECLARACION_ENUM` también nace en `1981904a` con un único tipo. No se
  halló un commit que añadiese o retirase un token/patrón inglés.
- La prueba de mezcla de aliases aparece en la versión actual de
  `tests/unit/test_parser.py`, ruta introducida en
  `b9b990ac218c8314f79121d6117a01ce68a06d17` (merge PR #3500). Su expectativa
  hace explícita la intención, pero la prueba falla actualmente.
- Las entradas del Libro proceden del índice autogenerado y `git blame` las
  atribuye a `b9b990ac...`, no a texto pedagógico escrito a mano.
- Búsquedas `git log -G/-S`, `git blame`, historial por archivo y revisión de
  todos los blobs históricos disponibles del lexer no encontraron una versión
  funcional de `enum`.

### Respuestas históricas

1. **¿`enum` llegó alguna vez a tokenizarse como `ENUMERACION`?** No en la
   historia disponible.
2. **¿Existe un commit donde fuese deliberadamente alias?** Existe evidencia de
   intención documental y de test (`1981904a`, después `b9b990ac`), pero no un
   commit con implementación léxica funcional.
3. **¿Apareció sólo en documentación/reservadas sin soporte real?** En el core
   ejecutable sí; adicionalmente apareció una prueba positiva de parser y
   maquinaria de advertencia, aunque ambas quedaron inoperantes para `enum`.
4. **¿Se rompió durante una refactorización?** No hay evidencia de rotura: la
   inconsistencia está ya en el primer snapshot de las rutas actuales y
   permanece estable.
5. **¿Hay evidencia suficiente para restaurarlo?** Hay evidencia suficiente de
   intención contractual para **completarlo** como compatibilidad, no para
   llamarlo “restauración” de una capacidad antes funcional.

### Límite de la historia

Aunque el repositorio local contiene 273 commits alcanzables, las rutas core
actuales comienzan en un merge masivo y no se halló una implementación anterior
equivalente bajo las rutas registradas. Por tanto, la conclusión “nunca fue
funcional” se limita estrictamente a la historia disponible; no se inventa una
intención anterior ni se descarta código que pudiera existir fuera del Git
provisto.

## Contradicciones encontradas

### Core vs docs

- El core acepta sólo `enumeracion`; la SPEC afirma explícitamente que acepta
  `enum` o `enumeracion` como sinónimos y que advierte al mezclarlos.
- La EBNF no define ninguna de las dos como declaración, pese a que
  `enumeracion` sí funciona en el core.

### Core vs reservadas

- `enum` está reservado semánticamente como nombre, pero léxicamente es un
  identificador ordinario y no inicia la construcción que justificaría la
  reserva.

### Core vs REPL

- Ambos coinciden en aceptar/resaltar sólo `enumeracion`; sin embargo, el REPL
  duplica accidentalmente esa regla y ninguno refleja el alias prometido por la
  SPEC.

### Core vs VS Code

- VS Code no resalta ni siquiera la forma core funcional `enumeracion`; tampoco
  resalta `enum`.

### Docs vs tests

- La prueba `test_parser_advertencia_alias_enum` coincide con la promesa de la
  SPEC, pero falla con el core actual.
- Los contratos léxicos omiten `enum`, mientras la prueba de reservadas incluye
  ambas formas. Son contratos parciales sobre propiedades diferentes y dejan
  visible la incoherencia.

### Documentación autogenerada vs normativa manual

- El Libro, fuente normativa prioritaria del repositorio, sólo hereda ambas
  palabras en un inventario autogenerado desde gramática + SPEC. No ofrece
  afirmación manual ni ejemplo que confirme el alias.
- La afirmación manual está en la SPEC, mientras su EBNF carece por completo de
  enum. El índice generado no debe contarse como una segunda fuente normativa
  independiente.

## Clasificación final

### **E — Implementación parcial**

No es A porque `enum` falla; no es B porque no existe evidencia de que antes
funcionara; y la evidencia supera C/D/F: la SPEC declara explícitamente la
sinonimia, el parser incorpora seguimiento y mensajes de mezcla de aliases,
reservadas incluye ambas formas y existe una prueba positiva que exige ese
comportamiento. Todos esos elementos convergen en una intención contractual,
pero el lexer nunca completó la conexión y la prueba quedó roja. La
implementación parcial parece existir desde su introducción, no ser una
regresión demostrada.

## Recomendación de siguiente microtarea (no implementada)

**Opción 1: restaurar `enum` como alias de compatibilidad**, entendiendo
“restaurar” como completar el contrato público pretendido, no como revertir una
regresión histórica probada. Mantener `enumeracion` como forma española
principal/canónica.

- **Confianza:** media-alta (0,82) en completar el alias; alta (0,95) en que no
  debe llamarse alias histórico roto.
- **Riesgo:** medio. Cambiar la clasificación léxica de `enum` puede afectar
  código que hoy lo use como expresión identificadora (aunque ya está prohibido
  como nombre de variable declarado). También debe evitarse ampliar sintaxis
  sin autorización explícita, pues la microtarea tocaría el lexer.
- **Archivos probablemente afectados:**
  `src/pcobra/cobra/core/lexer.py`, pruebas dirigidas nuevas o la corrección de
  la prueba existente, `src/pcobra/cobra/cli/repl/cobra_lexer.py`,
  `extensions/vscode/syntaxes/cobra.tmLanguage.json` y
  `docs/gramatica.ebnf`. Si el índice del Libro se regenera mediante el proceso
  oficial, sólo el artefacto generado resultante que corresponda. El parser ya
  conserva `token.valor`, por lo que debe comprobarse primero que no necesite
  cambio.
- **Archivos que NO deberían tocarse:** runtime, AST, backends/transpilers,
  `PALABRAS_RESERVADAS` (ya contiene ambas), dependencias, workflows y ejemplos
  no relacionados. No debe rebajarse la aserción de la prueba de mezcla ni
  cambiarse documentación para ocultar el fallo.

La microtarea debe solicitar autorización explícita para modificar el lexer,
añadir primero una prueba Lexer → Parser positiva de `enum`, conservar la de
`enumeracion`, verificar la advertencia al mezclarlas y tratar por separado el
soporte Rust de `NodoEnum`, que es otro hallazgo.
