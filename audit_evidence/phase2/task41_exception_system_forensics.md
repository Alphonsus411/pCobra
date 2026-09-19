# Task 41 — Auditoría forense E2E del sistema de excepciones

## 0. Alcance, método y revisión auditada

- **SHA inicial auditada:** `521c04bbab5caa4d026cac7e75dd4644fffc397c`.
- Rama local al iniciar: `work`; árbol limpio.
- Fecha de auditoría: 2026-09-19 (UTC).
- Esta tarea es exclusivamente de investigación. No se cambió comportamiento, lexer,
  parser, AST, runtime, backends, tooling, documentación normativa, tests,
  dependencias ni workflows. El único archivo creado es este informe.
- Se inspeccionó el código vigente y después se ejecutaron sondas directas. El informe
  histórico de Task 7 se usó sólo para la comparación final.

La conclusión principal es que la reparación histórica de los nombres de token sí está
vigente: la ruta pública `intentar/try` + `capturar/catch` + `lanzar/throw` alcanza AST y
runtime. No obstante, el contrato completo sigue siendo inconsistente: el parser acepta
un `try` sin manejador, permite `catch` sin nombre, no puede alcanzar `finalmente` sin un
`catch`, y los tres backends auditados descartan `bloque_finally`.

## 1. Inventario exacto de `TipoToken`

Definición inspeccionada: `src/pcobra/cobra/core/lexer.py`, clase `TipoToken`.

| Nombre consultado | ¿Miembro real? | Valor | Interpretación |
|---|---:|---|---|
| `INTENTAR` | sí | `"INTENTAR"` | token real y normalizado de `try`/`intentar` |
| `CAPTURAR` | sí | `"CAPTURAR"` | token real y normalizado de `catch`/`capturar` |
| `FINALMENTE` | sí | `"FINALMENTE"` | token real sólo para `finalmente` |
| `LANZAR` | sí | `"LANZAR"` | token real y normalizado de `throw`/`lanzar` |
| `TRY` | no | — | inexistente; `try` no crea este nombre |
| `CATCH` | no | — | inexistente; `catch` no crea este nombre |
| `FINALLY` | no | — | inexistente; `finally` tampoco es palabra clave |
| `THROW` | no | — | inexistente; `throw` no crea este nombre |

La comprobación ejecutable de `TipoToken.__members__` produjo exactamente cuatro
`True` para los nombres españoles y cuatro `False` para los ingleses.

## 2. Matriz de las ocho grafías del lexer core

Las reglas exactas están en `Lexer._inicializar_especificaciones`: hay reglas separadas
para los seis lexemas inglés/español de try, catch y throw; `finalmente` tiene una regla
propia; no hay regla para `finally`. La sonda `Lexer(palabra).analizar_token()` dio:

| Entrada | Token producido | Valor preservado | ¿Reconocida como keyword? | ¿IDENTIFICADOR? |
|---|---|---|---:|---:|
| `try` | `INTENTAR` | `try` | sí | no |
| `intentar` | `INTENTAR` | `intentar` | sí | no |
| `catch` | `CAPTURAR` | `catch` | sí | no |
| `capturar` | `CAPTURAR` | `capturar` | sí | no |
| `finally` | `IDENTIFICADOR` | `finally` | **no** | **sí** |
| `finalmente` | `FINALMENTE` | `finalmente` | sí | no |
| `throw` | `LANZAR` | `throw` | sí | no |
| `lanzar` | `LANZAR` | `lanzar` | sí | no |

Todos quedaron seguidos de `EOF`. Posiciones observadas para palabras aisladas: línea 1,
columna 1 para el lexema y columna posterior al lexema para `EOF`.

## 3. `PALABRAS_RESERVADAS`

El registro público está en `src/pcobra/cobra/core/utils.py`.

| Grafía | Presente | Coincide con lexer |
|---|---:|---:|
| `try`, `intentar` | sí, sí | sí |
| `catch`, `capturar` | sí, sí | sí |
| `finally`, `finalmente` | **no**, sí | sí: `finally` es identificador |
| `throw`, `lanzar` | sí, sí | sí |

No hay una palabra presente en este subconjunto del registro que el lexer deje como
identificador. El registro, por sí solo, no prueba que una construcción sea parseable.

## 4. Estado exacto de `declaracion_try_catch()`

La implementación vigente sólo consulta estos miembros relevantes:
`INTENTAR`, `CAPTURAR`, `FIN`, `EOF`, `IDENTIFICADOR` y `FINALMENTE`. No consulta
`TRY`, `CATCH` ni `FINALLY`.

Flujo real:

1. exige que el token inicial sea `INTENTAR` y avanza; por normalización sirve tanto
   `try` como `intentar`;
2. exige `:`;
3. parsea `bloque_try` hasta `CAPTURAR`, `FIN` o `EOF` (**no incluye
   `FINALMENTE`**), y valida el contrato común de bloque vacío;
4. si aparece `CAPTURAR`, lo consume; el nombre de excepción se consume sólo si el
   siguiente token es `IDENTIFICADOR`, por lo que el nombre es opcional en código;
5. exige `:` y parsea catch hasta `FIN`, `EOF` o `FINALMENTE`;
6. si aparece `FINALMENTE`, exige `:`, parsea hasta `FIN`/`EOF` y lo guarda;
7. exige un `FIN` mediante `_exigir_fin`;
8. construye `NodoTryCatch(bloque_try, nombre_exc, bloque_catch, bloque_finally)`.

Consecuencias demostradas:

- catch es **opcional en el parser**, aunque SPEC/EBNF/Libro lo hacen obligatorio;
- finally es opcional después de catch;
- `intentar ... finalmente ... fin` sin catch no llega al paso de finally porque
  `FINALMENTE` no delimita el bloque try;
- `intentar ... fin`, sin catch ni finally, sí produce un `NodoTryCatch`;
- el parser admite `capturar:` sin identificador, contra las gramáticas publicadas;
- no existe comprobación que exija al menos catch o finally.

## 5. Estado exacto de `declaracion_throw()`

La función compara exclusivamente con `TipoToken.LANZAR`, avanza y devuelve
`NodoThrow(self.expresion())`. No referencia `TipoToken.THROW`. Por la normalización del
lexer, `throw expr` y `lanzar expr` siguen la misma ruta. La expresión es la expresión
general del parser, no sólo una cadena ni un identificador.

## 6. Reproductores mínimos desde fuente

Se ejecutó cada muestra con `Lexer(codigo).analizar_token()` y
`Parser(tokens).parsear()` sin modificar código.

| Caso | Secuencia relevante | Resultado parser | Excepción/punto de fallo |
|---|---|---|---|
| español (`intentar/lanzar/capturar`) | `INTENTAR : LANZAR IDENTIFICADOR CAPTURAR IDENTIFICADOR : IMPRIMIR ... FIN EOF` | OK: un `NodoTryCatch`, try=1, nombre=`e`, catch=1, finally=0 | ninguna |
| inglés (`try/throw/catch`) | la misma secuencia normalizada | OK, mismos campos | ninguna |
| mixto 1 (`intentar/throw/capturar`) | la misma secuencia normalizada | OK, mismos campos | ninguna |
| mixto 2 (`try/lanzar/catch`) | la misma secuencia normalizada | OK, mismos campos | ninguna |

Esto demuestra que las mezclas funcionan técnicamente por normalización. SPEC anuncia
los pares de alias, pero no documenta expresamente una política de mezclas; por ello el
resultado se registra como comportamiento, no como nueva promesa normativa.

Reproductores adicionales:

| Entrada mínima | Resultado actual |
|---|---|
| `intentar: imprimir("x") fin` (con saltos de línea) | parsea; catch y finally vacíos |
| `intentar: imprimir("x") finalmente: imprimir("fin") fin` | `ParserError: Token inesperado en término: TipoToken.FINALMENTE` |
| variante con `finally:` tras catch | `finally` es `IDENTIFICADOR`; `ParserError: Token inesperado en término: TipoToken.DOSPUNTOS` |

## 7. Auditoría independiente de `finalmente`

La muestra solicitada con catch y finally:

```cobra
intentar:
    imprimir("x")
capturar e:
    imprimir(e)
finalmente:
    imprimir("fin")
fin
```

tokeniza `finalmente` como `FINALMENTE`, parsea correctamente y almacena una instrucción
en `NodoTryCatch.bloque_finally`. Por tanto, **sí es alcanzable desde fuente cuando hay
catch**. El alias inglés `finally` no existe en enum, lexer, reservadas, REPL, VS Code ni
contrato formal, y cae como identificador. No debe presentarse como alias oficial.

Sin catch, `finalmente` no es alcanzable por el defecto del delimitador del bloque try.
Además, aunque runtime ejecuta el bloque, Python, JavaScript y Rust lo ignoran al bajar
el AST. “Parsea con catch” no equivale a soporte E2E en todos los destinos.

## 8. AST real

La definición efectiva usada por parser, runtime y transpiladores está en
`src/pcobra/core/ast_nodes.py`:

- `NodoThrow`: campo `expresion: Any`.
- `NodoTryCatch`:
  - `bloque_try: NodoBloque`;
  - `nombre_excepcion: Optional[str] = None`;
  - `bloque_catch: NodoBloque = NodoBloque()`;
  - `bloque_finally: NodoBloque = NodoBloque()`.

`__post_init__` normaliza los tres bloques mediante `_asegurar_bloque`. El AST soporta
try/catch/finally y ausencia de catch, más capacidad que la gramática formal y, para
finally, más de lo que conservan los backends.

Existe una superficie histórica de imports (`core.ast_nodes` frente a
`pcobra.core.ast_nodes`) que puede crear identidades de clase distintas bajo el entorno
de tests; se observó directamente en `tests/unit/test_try_catch.py`.

## 9. Runtime / intérprete

`src/pcobra/core/interpreter.py` despacha:

- `NodoThrow` a `raise ExcepcionCobra(evaluar_expresion(nodo.expresion))`;
- `NodoTryCatch` a `ejecutar_try_catch`.

`ejecutar_try_catch` ejecuta try, captura **sólo** `ExcepcionCobra`, vincula `exc.valor`
al entorno actual si existe `nombre_excepcion`, ejecuta catch y ejecuta finally mediante
un `finally` Python real. Errores Python inesperados no se capturan. Si el AST no tiene
catch, la cláusula `except ExcepcionCobra` aun así consume la excepción y ejecuta una
lista vacía: un `try` desnudo puede silenciar un `lanzar`.

`tests/unit/test_try_catch.py::test_interpreter_try_catch` es runtime manual. El test
llamado `test_interpreter_intentar_lanzar_capturar` sí parsea fuente, pero descarta ese
AST y construye otro AST manual antes de ejecutar: no es un E2E real.

## 10. Backend Python

Registro: `TranspiladorPython.visit_try_catch = _visit_try_catch` y
`visit_throw = _visit_throw` en `to_python.py`.

Lowering real:

- `NodoThrow(expr)` → `raise Exception(<valor>)`;
- try → `try:` y sus instrucciones;
- si `bloque_catch` no está vacío → `except Exception` más ` as nombre` cuando existe;
- **no lee ni emite `bloque_finally`**.

Un AST manual con try, throw, catch y finally produjo Python con try/except, pero sin la
impresión de finally. `compile(codigo, "<exceptions>", "exec")` pasó: sintaxis válida no
significa conservación semántica. Un AST permitido por el parser sin catch genera un
`try:` sin `except`/`finally`, que es sintaxis Python inválida.

Clasificación del backend: **parcial**.

## 11. Backend JavaScript

Registro equivalente en `to_js.py`.

Lowering real:

- `NodoThrow(expr)` → `throw <valor>;` (no envuelve en `Error`);
- emite `try { ... }`;
- con catch no vacío emite `catch (<nombre o cadena vacía>) { ... }`;
- **no lee ni emite `bloque_finally`**;
- sin catch emite sólo `try { ... }`, sintaxis inválida; con catch sin nombre pero no
  vacío puede emitir `catch ()`, también inválido.

El AST manual representativo con nombre y catch no vacío pasó `node --check`, pero el
finally presente en el AST desapareció. Clasificación: **parcial**.

## 12. Backend Rust y scopes

Registro equivalente en `to_rust.py`. Lowering:

1. crea una closure inmediatamente invocada con tipo
   `Result<(), Box<dyn std::error::Error>>`;
2. `NodoThrow(expr)` produce `return Err(<valor>.into());`;
3. añade `Ok(())` al final;
4. hace `match resultado`, con `Ok(_) => ()` y `Err(e) => { ...catch... }`;
5. si hay nombre, genera `let nombre = e;`;
6. **ignora `bloque_finally`**.

No son excepciones equivalentes: sólo errores retornados dentro de la closure entran en
el `Err`; panics y errores ajenos no se capturan. La conversión `.into()` restringe los
valores a tipos convertibles al error boxed. El archivo completo emitido por
`generate_code` falló `rustc --edition 2021` porque coloca `let resultado` a nivel de
módulo (`expected item, found keyword let`). El fragmento de excepción envuelto en
`fn main()` sí compiló y ejecutó bajo la restricción de un literal `&str` convertible,
imprimiendo `fallo`. Compilabilidad bajo envoltura no implica equivalencia semántica.

`visit_try_catch` usa `with self._enum_scope(nodo.bloque_try)` y otro contexto separado
para `nodo.bloque_catch`: los scopes de enumeraciones de try y catch sí están separados.
No usa `_enum_scope` para finally porque no lo recorre. Scope correcto y semántica de
excepciones siguen siendo cuestiones separadas.

Clasificación solicitada del backend Rust: **parcial**, no equivalente ni aproximación
documentada completa.

## 13. REPL / Pygments

`src/pcobra/cobra/cli/repl/cobra_lexer.py` contiene reglas `Keyword` para:
`try`, `intentar`, `catch`, `capturar`, `throw`, `lanzar` y `finalmente`, mapeadas a los
mismos tokens canónicos que el core. No contiene `finally`. En este subconjunto está
alineado con el lexer core; el indicio histórico de que sólo resaltaba inglés ya no se
cumple.

## 14. VS Code

`extensions/vscode/syntaxes/cobra.tmLanguage.json` incluye en una expresión con scope
`keyword.control.cobra`: `try`, `intentar`, `catch`, `capturar`, `throw`, `lanzar` y
`finalmente`. No incluye `finally`. Coincide con lexer y REPL para las ocho grafías.

## 15. SPEC

`docs/SPEC_COBRA.md` publica:

- producción `try_catch: ("try"|"intentar") ... ("catch"|"capturar")
  IDENTIFICADOR ... "fin"`;
- lista explícita de pares `try/intentar`, `catch/capturar`, `throw/lanzar`;
- ejemplo inglés completo y texto que autoriza las formas españolas;
- descripción runtime de `ExcepcionCobra`;
- `finalmente` en la lista general de palabras, pero no en la producción, explicación ni
  ejemplo de excepciones;
- ninguna forma `finally`, política explícita de mezclas ni deprecación.

Contradicciones: la producción hace catch y su identificador obligatorios, pero el
parser permite omitir ambos; `finalmente` aparece publicado como keyword sin sintaxis
formal en esta sección.

## 16. EBNF

`docs/gramatica.ebnf` sí tiene producciones para try/catch y throw/lanzar. Acepta los
pares ingleses/españoles de los tres conceptos, requiere catch + `IDENTIFICADOR`, termina
en `fin`, y no contiene `finalmente` ni `finally`. Contradice al parser vigente en la
opcionalidad de catch/nombre, y omite una ruta que el parser acepta después de catch.

## 17. Libro normativo y otra documentación

`docs/LIBRO_PROGRAMACION_COBRA.md` es la fuente normativa indicada por `AGENTS.md`.

- **Correcta/canónica:** la sintaxis formal simplificada usa exclusivamente
  `intentar`, `capturar IDENTIFICADOR` y `lanzar`; los ejemplos usan español.
- **Aliases presentes pero ambiguos en esta sección:** el inventario global incluye
  también `try`, `catch` y `throw`, pero la sección 3.7 no los declara aliases ni enseña
  mezclas. SPEC sí los anuncia explícitamente.
- **`finalmente` ambiguo/incompleto:** figura en el inventario global, pero falta en la
  producción y ejemplos de errores. `finally` no figura.
- **Obsoleto/incompleto respecto al parser:** la producción exige catch/nombre y no
  muestra el `fin` que el parser exige; el primer ejemplo tampoco muestra `fin`.
- La nota “modelos de excepción varían” es correcta como advertencia general, pero no
  documenta que los tres backends descarten finally.

`python scripts/sync_libro_programacion.py --check` informó `Sin drift documental`; esto
comprueba sincronización del artefacto, no coherencia semántica.

## 18. Matriz de tests existentes

| Archivo/caso | Clasificación | Qué cubre / qué no cubre |
|---|---|---|
| `tests/test_lexer_parser_contract.py` | lexer directo/contrato | seis aliases y `finalmente`; no prueba `finally` ni E2E |
| `tests/unit/test_try_catch.py::test_parser_try_catch_throw` | parser con tokens manuales | no ejercita lexer; hoy falla por identidad duplicada de AST |
| `tests/unit/test_try_catch.py::test_parser_intentar_lanzar_capturar` | fuente→parser | ejercita frontend; falla en `isinstance` por namespaces |
| `tests/unit/parser_test_constructs.py::test_parser_intentar_capturar` | fuente→parser | compara AST; no runtime/backend |
| `tests/unit/test_try_catch.py::test_interpreter_try_catch` | runtime manual | AST construido manualmente |
| `test_interpreter_intentar_lanzar_capturar` | parser + runtime manual separados | descarta el AST parseado; no E2E |
| `tests/unit/test_to_python_extras.py::test_transpilar_try_catch_throw` | backend manual | AST manual; no finally |
| `tests/unit/test_try_catch.py` transpilers | backend manual | AST manual/imports históricos; no finally |
| `tests/unit/test_to_rust.py::test_try_catch_result` | backend manual | AST manual; snapshot hoy desalineado por prelude; no rustc/finally |
| `tests/unit/test_transpiler_feature_parity.py` | contrato backend manual | fixture AST manual, `bloque_finally=[]`; filtro recomendado selecciona 0 por parametrización |
| `tests/integration/transpilers/test_language_equivalence_contract.py` | backend manual/golden | fixture AST manual; no fuente Cobra |
| `test_language_equivalence_feature_contracts.py` | backend manual/golden | fixture AST manual; no fuente Cobra |
| golden `*.manejo_errores.golden` | documentación/snapshot de backend | salida esperada de AST manual, no parser ni ejecución E2E |
| `tests/unit/test_to_js.py` | no relacionado con excepciones Cobra | coincidencias `try/finally` son Python del propio test o lowering de defer, no `NodoTryCatch` |

No se localizó cobertura que pruebe `finalmente` desde fuente hasta runtime/backend, un
try sin catch, un catch sin nombre o el rechazo explícito de `finally`. Tampoco se halló
un E2E real fuente→lexer→parser→AST→ejecución de excepciones: el caso cuyo nombre lo
sugiere reconstruye manualmente el nodo.

## 19. Resultados de comandos recomendados

| Comando | Salida resumida | Código |
|---|---|---:|
| `pytest -q tests/unit/test_try_catch.py` | 2 passed, 4 failed: 2 identidades AST y 2 `constant_folder` sobre namespace histórico | 1 |
| `pytest -q tests/test_lexer_parser_contract.py` | 5 passed | 0 |
| `pytest -q tests/unit/test_parser.py -k "try or catch or throw or intentar or capturar or lanzar or finalmente"` | **10 deselected, 0 selected**; no se cuenta como passed | 5 |
| `pytest -q tests/unit/test_to_python_extras.py -k "try or catch or throw"` | 1 passed, 4 deselected | 0 |
| `pytest -q tests/unit/test_to_js.py -k "try or catch or throw"` | **19 deselected, 0 selected** | 5 |
| `pytest -q tests/unit/test_to_rust.py -k "try or catch or throw"` | 1 failed, 19 deselected; salida tiene prelude no esperado | 1 |
| `pytest -q tests/unit/test_transpiler_feature_parity.py -k "try or catch or throw"` | **41 deselected, 0 selected** | 5 |
| `python scripts/sync_libro_programacion.py --check` | `Sin drift documental.` | 0 |

`git diff --check` y las verificaciones finales se registran en la sección 26 después de
materializar el informe.

## 20. Validaciones de destino

| Destino | Entrada | Validación | Resultado y límite |
|---|---|---|---|
| Python | AST manual con try/throw/catch/finally | `compile(..., "<exceptions>", "exec")` | pasa, pero finally fue omitido |
| JavaScript | mismo AST manual | `node --check /tmp/task41.js` | pasa, pero finally fue omitido |
| Rust | salida completa de `generate_code` | `rustc --edition 2021 /tmp/task41.rs` | falla: sentencia `let` a nivel módulo |
| Rust | fragmento generado envuelto en `fn main()` | `rustc --edition 2021 ...` y ejecución | pasa/imprime `fallo` para `&str`; aproximación Result, sin finally |

## 21. Comparación con Task 7

| Hallazgo histórico | Estado actual | Dictamen |
|---|---|---|
| no existen `TRY`, `CATCH`, `THROW` | siguen sin existir; tampoco `FINALLY` | sigue vigente como diseño de normalización |
| lexer normaliza aliases a tokens españoles | confirmado para los seis lexemas | sigue vigente |
| parser referenciaba miembros inexistentes antes de #3582 | ahora usa sólo `INTENTAR`, `CAPTURAR`, `LANZAR` | **corregido** |
| test manual usaba tipos ingleses inexistentes | usa tipos normalizados | corregido |
| fallos independientes de identidad AST/constant folder | reaparecen en la suite focal (4 fallos) | siguen vigentes, fuera de la reparación Task 7 |

Task 7 acertó al cerrar la desalineación específica de enum. No auditó ni resolvió las
inconsistencias de finally, opcionalidad o lowering encontradas aquí.

## 22. Hallazgos individualizados

### EXC-001 — `try` desnudo aceptado y excepción silenciada

- **Gravedad:** alta.
- **Superficie:** parser/runtime/backends.
- **Archivo/símbolo:** `parser.py::declaracion_try_catch`,
  `interpreter.py::ejecutar_try_catch`.
- **Entrada mínima:** `intentar:\n imprimir("x")\nfin` (y, para semántica,
  reemplazar imprimir por `lanzar "x"`).
- **Actual:** parser crea catch/finally vacíos; runtime consume `ExcepcionCobra`; Python y
  JS pueden generar un try sintácticamente inválido.
- **Esperado:** conforme a Libro/SPEC/EBNF, exigir catch con nombre; si se decide ampliar
  el lenguaje, exigir al menos catch o finally y documentarlo.
- **Causa probable:** listas vacías usadas como defaults sin validación estructural.
- **Alcance mínimo:** parser (bloqueado por restricción de esta auditoría) y tests E2E;
  revisar runtime/backends según contrato decidido.

### EXC-002 — catch sin nombre contradice la gramática

- **Gravedad:** alta para JS, media para frontend.
- **Superficie:** parser/JS/documentación.
- **Archivo/símbolo:** `parser.py::declaracion_try_catch`,
  `js_nodes/try_catch.py::visit_try_catch`.
- **Entrada mínima:** `intentar:\n lanzar "x"\ncapturar:\n imprimir("x")\nfin`.
- **Actual:** parser admite `nombre_excepcion=None`; JS con catch no vacío emite
  `catch ()`, inválido.
- **Esperado:** Libro/SPEC/EBNF requieren `IDENTIFICADOR`.
- **Causa probable:** consumo condicional del identificador y concatenación vacía JS.
- **Alcance mínimo:** normalización parser y prueba fuente→JS→`node --check`.

### EXC-003 — finally sin catch es inalcanzable

- **Gravedad:** media.
- **Superficie:** parser.
- **Archivo/símbolo:** `parser.py::declaracion_try_catch`.
- **Entrada mínima:** `intentar:\n imprimir("x")\nfinalmente:\n imprimir("fin")\nfin`.
- **Actual:** `ParserError: Token inesperado en término: TipoToken.FINALMENTE`.
- **Esperado:** la estructura del método y AST sugieren finally opcional sin catch; si no
  se desea soportar, rechazarlo de forma contractual y no insinuarlo como alternativa.
- **Causa probable:** `FINALMENTE` falta entre terminadores de `bloque_try`.
- **Alcance mínimo:** decisión normativa primero; después parser + test focal. Requiere
  tocar parser, por lo que queda bloqueado en esta tarea.

### EXC-004 — backend Python descarta finally

- **Gravedad:** alta.
- **Superficie:** Python.
- **Archivo/símbolo:** `python_nodes/try_catch.py::visit_try_catch`.
- **Entrada mínima:** muestra de sección 7 o AST con `bloque_finally` no vacío.
- **Actual:** código compila pero no contiene ni ejecuta `finally`.
- **Esperado:** emitir `finally:` y el bloque conservando semántica.
- **Causa probable:** visitante anterior a la ampliación del AST/parser.
- **Alcance mínimo:** visitante Python + tests backend y E2E, sin cambiar sintaxis.

### EXC-005 — backend JavaScript descarta finally

- **Gravedad:** alta.
- **Superficie:** JavaScript.
- **Archivo/símbolo:** `js_nodes/try_catch.py::visit_try_catch`.
- **Entrada mínima:** muestra de sección 7.
- **Actual:** `node --check` pasa para try/catch, pero no se emite `finally`.
- **Esperado:** `finally { ... }`.
- **Causa probable:** visitante incompleto.
- **Alcance mínimo:** visitante JS + `node --check` y prueba de ejecución.

### EXC-006 — backend Rust descarta finally y no es excepción equivalente

- **Gravedad:** alta.
- **Superficie:** Rust.
- **Archivo/símbolo:** `rust_nodes/try_catch.py`, `rust_nodes/throw.py`.
- **Entrada mínima:** AST manual con throw/catch/finally.
- **Actual:** aproximación mediante `Result`, no captura panic, restringe `.into()` y
  descarta finally; la salida completa auditada tampoco compila como crate por sentencias
  a nivel módulo.
- **Esperado:** contrato de aproximación explícito y preservación garantizada de finally,
  con una unidad compilable en el contexto soportado.
- **Causa probable:** mapeo parcial de excepciones a `Result`.
- **Alcance mínimo:** especificar restricciones; visitante Rust + harness `rustc`.

### EXC-007 — gramáticas/documentación divergen del frontend

- **Gravedad:** media.
- **Superficie:** SPEC/EBNF/Libro.
- **Archivo/símbolo:** producciones `try_catch` y sección 3.7.
- **Entrada mínima:** comparar try sin catch, catch sin nombre y finally tras catch.
- **Actual:** gramáticas requieren catch+nombre y omiten finally; parser permite los dos
  primeros y admite finally tras catch. Libro omite además `fin` en ejemplos/producción.
- **Esperado:** una única política normativa coherente con implementación verificada.
- **Causa probable:** evolución no sincronizada de parser y documentos.
- **Alcance mínimo:** resolver primero frontend/semántica; luego actualización documental
  separada mediante el proceso normativo, nunca para ocultar fallos.

### EXC-008 — suite focal mezcla namespaces AST

- **Gravedad:** media (calidad/CI).
- **Superficie:** tests e imports históricos.
- **Archivo/símbolo:** `tests/unit/test_try_catch.py`.
- **Entrada mínima:** `pytest -q tests/unit/test_try_catch.py`.
- **Actual:** 4 fallos: dos objetos visualmente `NodoTryCatch` no satisfacen
  `isinstance`, y dos AST manuales son rechazados por `constant_folder`.
- **Esperado:** una identidad canónica de clases en la prueba y pipeline backend.
- **Causa probable:** mezcla `cobra.core`, `core.ast_nodes` y rutas `pcobra.*`.
- **Alcance mínimo:** microtarea independiente de imports/compatibilidad; no reducir
  aserciones ni ocultar errores.

### EXC-009 — ausencia de cobertura E2E y finally

- **Gravedad:** media.
- **Superficie:** tests.
- **Archivo/símbolo:** suites de parser/runtime/transpiladores.
- **Entrada mínima:** muestra de sección 7 y los cuatro reproductores de sección 6.
- **Actual:** predominan tokens o AST manuales; el supuesto test intérprete E2E descarta
  el AST fuente; no hay prueba de finally ni validaciones destino integradas.
- **Esperado:** matriz fuente→lexer→parser→AST→runtime/backend para grafías soportadas y
  casos estructurales.
- **Causa probable:** cobertura fragmentada por capa.
- **Alcance mínimo:** añadir pruebas después de fijar contrato, sin cambiar producción en
  la misma microtarea.

## 23. Clasificación individual

| Construcción | Clase | Fundamento |
|---|---|---|
| `intentar/try` | **C — parcial** | aliases, parser y AST funcionan, pero try desnudo se admite y rompe/silencia según destino |
| `capturar/catch` | **C — parcial** | normalización funciona; opcionalidad y nombre contradicen contrato y pueden romper JS |
| `finalmente` (`finally` no existe) | **D — inconsistente** | token/AST/parser tras catch/runtime existen, pero ruta sin catch falla, docs formales omiten y backends lo descartan |
| `lanzar/throw` | **B — funcional con deuda no bloqueante** | frontend/runtime/Python/JS funcionan en su contrato básico; Rust es aproximación restringida |

El inglés `finally` se clasifica como **E — no implementado**, no como alias roto: no hay
evidencia normativa ni de implementación que lo anuncie.

## 24. Clasificación global

**D — inconsistente.** La ruta pública básica con catch funciona, pero el sistema
completo no preserva finalmente en ningún backend auditado, acepta estructuras contrarias
a las gramáticas y carece de E2E que detecte estas divergencias. Nodos y visitantes
aislados no elevan la clasificación.

## 25. Orden mínimo recomendado de microtareas posteriores

1. **41A — fijar contrato estructural try/catch/finalmente:** decidir, desde el Libro,
   obligatoriedad de catch/nombre y validez de only-finally; bloquear si exige parser.
2. **41B — alinear parser con el contrato:** una reparación focal de opcionalidad,
   identificador y delimitador `FINALMENTE`; no tocar lexer ni añadir aliases.
3. **41C — preservar finally en runtime/backends:** Python, JS y Rust como hallazgos
   independientes, con validación de ejecución/compilación.
4. **41D — especificar la aproximación Rust:** tipos convertibles, contexto de función,
   panic frente a `Err` y forma de finally.
5. **41E — sanear identidad AST de la suite focal:** imports canónicos/compatibilidad,
   separado del comportamiento de excepciones.
6. **41F — matriz E2E:** español, inglés y mezclas ya admitidas; catch requerido/sin
   nombre según contrato; finally; runtime; `compile`, `node --check` y `rustc`.
7. **41G — sincronización documental/tooling:** sólo tras estabilizar conducta; SPEC,
   EBNF y Libro. REPL/VS Code no necesitan cambio para las grafías actuales.

## 26. Archivos modificados y controles finales

- Único archivo añadido: `audit_evidence/phase2/task41_exception_system_forensics.md`.
- Ningún archivo preexistente fue modificado.
- `git diff --cached --check` terminó con código 0 antes del commit.
- Se verificó por el diff preparado que `lexer.py` y `parser.py` permanecen intactos.
- El SHA final y la referencia de PR se consignan en la entrega externa después del
  commit y creación de PR, no se anticipan dentro de la evidencia auditada.
