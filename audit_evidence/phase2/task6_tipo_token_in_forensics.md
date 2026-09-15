# Phase 2 — Task 6: forense de TipoToken.IN

## 1. SHA auditado

La revisión se realizó sobre el commit exacto `00970036c24a364fd6de239e8033277d4d473736`, en la rama local `work`. Este commit es el merge de la PR #3580 y tiene como padres `e98b567d4d48fb2c73234ffdc5eafa3d201fbe65` y `c14ccb26e40620fc2d7ce9124e6bac2b21e27224`. El árbol de trabajo estaba limpio al comenzar la auditoría.

La secuencia inmediatamente anterior de interés es: merge de #3578 (`89e90fefa27dbf079ec9ad94e5898d44d212c581`), merge de #3579 (`e98b567d4d48fb2c73234ffdc5eafa3d201fbe65`) y merge de #3580 (`00970036c24a364fd6de239e8033277d4d473736`).

## 2. Entorno

- Repositorio: `Alphonsus411/pCobra`, copia local en `/workspace/pCobra`.
- Rama auditada: `work`.
- Fecha de comprobación: 2026-09-15 (UTC).
- Las pruebas se ejecutaron con `python -m pytest` en el entorno Python disponible del repositorio.
- La información de las PR se contrastó con los commits locales y con la API pública de GitHub. El estado de Actions se consultó para el SHA auditado; no se equipara el éxito de un workflow focal con un CI global verde.

## 3. Fallo original

En el padre base de #3578, `ee45c3d1887b8b33fa3c66bdff0bd02e9e725195`, `tests/unit/test_parser_error_reporting.py::test_error_en_declaracion_para` construía esta lista antes de instanciar el parser:

```python
Token(TipoToken.PARA, "para"),
Token(TipoToken.IDENTIFICADOR, "i"),
Token(TipoToken.IN, "in"),
Token(TipoToken.IDENTIFICADOR, "nums"),
```

La evaluación de los argumentos de `Token(...)` exige resolver primero el atributo `TipoToken.IN`. Como `IN` no es miembro de `TipoToken`, el mecanismo de acceso a atributos de `Enum` lanza `AttributeError: IN`. Esto sucede mientras se construye la lista `tokens`, antes de llegar a `parser = Parser(tokens)` y, con mayor razón, antes de `Parser.parsear()`.

Por tanto, el fallo original no demostraba por sí mismo un defecto del parser ni ejercitaba la aserción de diagnóstico que pretendía comprobar el test (la ausencia de `:` después del iterable). Era un fallo de preparación del test causado por una expectativa histórica obsoleta.

## 4. TipoToken actual

La definición real está en `src/pcobra/cobra/core/lexer.py`, en `class TipoToken(Enum)`. En el SHA auditado:

- existe `TipoToken.EN`;
- su valor asociado es la cadena `"EN"`;
- existe `TipoToken.PARA`, con valor `"PARA"`, como token de inicio del bucle;
- no existe ningún miembro `TipoToken.IN` (tampoco un alias con ese nombre).

Una comprobación directa de `TipoToken.__members__` devolvió `False` para `"IN"`; `TipoToken.EN.value` devolvió `EN`. No se modificó el enum durante esta microtarea.

## 5. Contrato del lexer

El lexer clásico registra explícitamente:

```python
(TipoToken.PARA, re.compile(r"\bpara\b")),
...
(TipoToken.EN, re.compile(r"\ben\b")),
```

No registra una regla de palabra reservada para `in`. Debido a que la regla general de identificadores sí admite esa secuencia, la comprobación directa produjo:

- `en` → `Token` de tipo `EN`, valor `"en"`, seguido de `EOF`;
- `in` → `Token` de tipo `IDENTIFICADOR`, valor `"in"`, seguido de `EOF`.

El contrato automatizado de palabras clave en `tests/test_lexer_parser_contract.py` también mapea `"en"` a `TipoToken.EN` y lista `EN` entre los tokens contextuales que el parser soporta. Nada de ello ofrece `in` como alias vigente. No se modificó el lexer.

## 6. Contrato del parser

La implementación real de `Parser.declaracion_para()` consume, en orden, `TipoToken.PARA`, un `TipoToken.IDENTIFICADOR` para la variable de iteración y, entre esa variable y la expresión iterable, exige `TipoToken.EN`. Si el token no es `EN`, reporta `Se esperaba 'en' después del identificador en 'para'`; si lo es, ejecuta `self.comer(TipoToken.EN)` y continúa con `self.expresion()`.

En consecuencia, el separador contractual entre variable e iterable es `TipoToken.EN`; el parser no espera `TipoToken.IN`. No se modificó el parser.

## 7. Sintaxis normativa de `para`

La fuente normativa indicada por el repositorio, `docs/LIBRO_PROGRAMACION_COBRA.md`, muestra en §4.3 y §4.4:

```cobra
para nombre en nombres:
    imprimir(nombre)
```

```cobra
para n en [1,2,3,4,5]:
    ...
```

Esta forma `para i en iterable` coincide con el enum, el lexer, el parser y los tests vigentes reparados. También aparece en pruebas actuales como `tests/unit/test_interpreter_para.py`, `tests/unit/test_ast_contract.py` y `tests/unit/parser_test_constructs.py`.

Persisten referencias textuales históricas a `in`, entre ellas `docs/gramatica.ebnf`, `docs/SPEC_COBRA.md`, la gramática de resaltado de VS Code y casos de rechazo como `tests/unit/test_parser_block_contract.py` o `tests/unit/parser_error_handling.py`. No son la fuente normativa para esta auditoría y no anulan el contrato ejecutable y normativo anterior. Se registran como residuos históricos o contextos de rechazo, no como prueba de que `TipoToken.IN` deba existir. Corregirlos o reclasificarlos individualmente queda fuera del alcance de esta tarea documental.

## 8. Causa raíz

La causa raíz fue una **expectativa de test obsoleta**: el test ensamblaba manualmente un miembro de enum inexistente (`TipoToken.IN`) y el lexema histórico `"in"`, mientras que el contrato vigente usa `TipoToken.EN` y `"en"`.

La excepción se originaba en el acceso al miembro inexistente del enum, durante la evaluación de `TipoToken.IN`. Al ocurrir antes de crear el `Parser`, no podía informar sobre el comportamiento de `Parser.parsear()`. La solución adecuada era alinear los tests de aceptación con el contrato ya existente, no añadir un token/alias, ni modificar lexer o parser.

## 9. PR #3578

- **Base:** `ee45c3d1887b8b33fa3c66bdff0bd02e9e725195` (`master`).
- **Head:** `828081d0088a7364635244f28fa08155ef7e27af`.
- **Merge:** `89e90fefa27dbf079ec9ad94e5898d44d212c581`.
- **Archivo modificado:** `tests/unit/test_parser_error_reporting.py` únicamente.
- **Cambio:** sustituyó `Token(TipoToken.IN, "in")` por `Token(TipoToken.EN, "en")` en `test_error_en_declaracion_para`. Así el test alcanzó `Parser.parsear()` y volvió a comprobar el error esperado por la ausencia de `:`.
- **Producción / Lexer / Parser:** no tocó producción, lexer ni parser.
- **Pruebas reportadas en la PR:** pasaron `pytest -vv tests/unit/test_parser_error_reporting.py::test_error_en_declaracion_para`, el archivo completo `tests/unit/test_parser_error_reporting.py` y `pytest -vv tests/unit/test_parser_block_contract.py -k iterable`.
- **Riesgos/hallazgos independientes reportados:** una ejecución relacionada más amplia mostró cuatro fallos preexistentes por referencias a tokens o sintaxis obsoletos. El texto de la PR no identifica sus nodeids, por lo que este informe no los atribuye ni diagnostica con más precisión.

## 10. PR #3579

- **Base:** `89e90fefa27dbf079ec9ad94e5898d44d212c581` (`master`).
- **Head:** `59f22a53424b34335aa72a111480bef9301f59ba`.
- **Merge:** `e98b567d4d48fb2c73234ffdc5eafa3d201fbe65`.
- **Archivo modificado:** `tests/unit/test_parser_para_long_loop.py` únicamente.
- **Cambio:** sustituyó `Token(TipoToken.IN, "in")` por `Token(TipoToken.EN, "en")`, conservando las 1001 sentencias y las aserciones de la prueba de estrés.
- **Producción / Lexer / Parser:** no tocó producción, lexer ni parser.
- **Pruebas reportadas en la PR:** la prueba focal pasó (`1 passed`). En una ejecución conjunta, la prueba larga pasó y `tests/unit/parser_test_constructs.py::test_parser_para` falló porque aún contenía un ejemplo válido escrito con `in`.
- **Riesgo/hallazgo independiente reportado:** quedaban otros ejemplos válidos desalineados con `en`; #3579 no amplió su alcance y el residuo señalado se trató después en #3580.

## 11. PR #3580

- **Base:** `e98b567d4d48fb2c73234ffdc5eafa3d201fbe65` (`master`).
- **Head:** `c14ccb26e40620fc2d7ce9124e6bac2b21e27224`.
- **Merge:** `00970036c24a364fd6de239e8033277d4d473736`.
- **Archivos modificados:** `tests/unit/parser_test_constructs.py`, `tests/unit/test_parser5.py`, `tests/unit/test_parser_consistencia_ast.py` y `tests/unit/test_romper_continuar.py`.
- **Cambio:** sustituyó por `en` cinco separadores textuales `in` en fragmentos que pretendían ser sintaxis válida; no cambió casos destinados a comprobar rechazo.
- **Producción / Lexer / Parser:** no tocó producción, lexer ni parser; tampoco añadió tokens, aliases o reglas gramaticales.
- **Pruebas reportadas en la PR:** `tests/unit/test_interpreter_para.py` pasó (4 pruebas). Las suites restantes reportaron fallos independientes: tres en `test_romper_continuar.py`, uno en `test_parser_consistencia_ast.py`, uno de tres en `parser_error_handling.py`, tres en `parser_test_constructs.py`, uno de trece en `test_parser_block_contract.py` y cuatro en `test_parser5.py`. `git diff --check` pasó.
- **Riesgos/hallazgos independientes reportados:** identidad/repr de AST, `constant_folder`, `LarkParser`/`UnexpectedCharacters` y `TipoToken.TRY`; ninguno se corrigió ni debe imputarse a `TipoToken.IN`.

## 12. Pruebas focales

Reejecutadas sobre `00970036c24a364fd6de239e8033277d4d473736`:

| Comando | Resultado |
|---|---|
| `python -m pytest -q tests/unit/test_parser_error_reporting.py::test_error_en_declaracion_para` | `1 passed in 0.30s` |
| `python -m pytest -q tests/unit/test_parser_para_long_loop.py::test_parser_para_mas_de_mil_sentencias` | `1 passed in 0.21s` |
| `python -m pytest -q tests/unit/test_interpreter_para.py` | `4 passed in 0.91s` |

La primera prueba ahora construye tokens con `EN`, entra en `Parser.parsear()` y valida el diagnóstico por `:` ausente. La segunda confirma que el cambio no redujo el cuerpo de 1001 sentencias. La tercera aporta evidencia de ejecución extremo a extremo del bucle `para` con sintaxis `en`. No se modificó código como consecuencia de estos resultados.

## 13. Estado de Runtime Stabilization Contract

Para el SHA posterior a las tres reparaciones, `00970036c24a364fd6de239e8033277d4d473736`, GitHub Actions registra el workflow **Runtime Stabilization Contract** (evento `push`) como `completed/success`, run `34975144378`; su job `runtime-stabilization-contract` también terminó en `success`.

En combinación con las pruebas focales locales, esto confirma que el bloqueo `AttributeError: IN` ya no está presente en la ruta reparada y que el workflow focal pasó. No significa CI global verde: para el mismo SHA aparecen fallos en los workflows `Lint`, `CI`, `Build & Release CLI Binaries`, `tests`, `Deploy Docs` y `CodeQL`. GitHub registra esos estados, pero esta auditoría no inspecciona ni diagnostica sus causas; no deben mezclarse automáticamente con Task 6.

Referencia verificable: <https://github.com/Alphonsus411/pCobra/actions/runs/34975144378>.

## 14. Clasificación final

**EXPECTATIVA DE TEST OBSOLETA — CERRADO**

La clasificación se sustenta en que `TipoToken.IN` no pertenece al enum vigente; `TipoToken.EN` sí existe con valor `"EN"`; el lexer reconoce `en` como `EN` y no reserva `in`; el parser exige `EN`; el Libro prescribe `para ... en ...`; #3578–#3580 alinearon exclusivamente pruebas con ese contrato, sin cambios de producción, lexer o parser; y las pruebas focales y el workflow contractual pasan.

## 15. Problemas independientes fuera de alcance

Se dejan expresamente separados, sin diagnóstico profundo ni corrección:

- referencias a `TipoToken.TRY` pese a que el enum actual expone `INTENTAR`;
- discrepancias de identidad y/o `repr` entre instancias de nodos AST y expectativas de algunas pruebas;
- fallos relacionados con `constant_folder`;
- diferencias del `LarkParser`, incluida `UnexpectedCharacters`;
- residuos históricos de texto `in` en documentos no normativos, resaltado y casos de rechazo;
- cualquier otro fallo de workflows del SHA auditado.

Estos hallazgos no son evidencia de que deba restaurarse `TipoToken.IN`, no forman parte de #3578–#3580 y deben investigarse en tareas separadas.

## 16. Conclusión

`TipoToken.IN` era una expectativa histórica obsoleta. El contrato actual utiliza `TipoToken.EN`, y la sintaxis vigente utiliza `en` como separador de la variable y el iterable en `para`. El fallo original ocurría al acceder al miembro inexistente del enum, antes de instanciar el parser y antes de `Parser.parsear()`, por lo que no probaba un defecto del parser.

No fue necesario modificar Lexer ni Parser: #3578 corrigió el test de reporte de errores, #3579 corrigió la prueba larga y #3580 alineó los ejemplos sintácticos válidos restantes identificados en esas pruebas. Las comprobaciones focales y Runtime Stabilization Contract confirman que esa corrección fue adecuada. Task 6 puede cerrarse como **EXPECTATIVA DE TEST OBSOLETA — CERRADO**. Los demás fallos observados —`TipoToken.TRY`, identidad/repr AST, `constant_folder`, LarkParser/`UnexpectedCharacters` y otros estados de CI— son independientes y deben investigarse en tareas separadas.
