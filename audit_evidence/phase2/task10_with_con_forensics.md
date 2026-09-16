# Phase 2 — Task 10: forense de WITH/CON

## 1. SHA auditado

El estado auditado es el commit de merge `58706c4ceb9c27b392e610505955fc647fbff4b5`,
en la rama local `work`. La trazabilidad de la PR #3586 es:

- base: `54b4dc6232833ccabd21682c3238732675be6e51`;
- head: `30394be5a2e670f5b3f00a02943a0a09ae8ff8f4`;
- merge: `58706c4ceb9c27b392e610505955fc647fbff4b5`.

Al iniciar la auditoría, `git status --short` no produjo salida: el árbol de
trabajo estaba limpio.

## 2. Entorno

La comprobación se realizó el 16 de septiembre de 2026 en Linux x86_64, con
Python 3.12.13 y pytest 9.0.3. La inspección histórica se hizo directamente
sobre los objetos Git indicados, sin restaurar ni modificar sus archivos.

## 3. Fallo original

En la base de la PR, el test
`tests/unit/test_nuevos_tokens.py::test_lexer_palabras_nuevas_en` analizaba:

```python
codigo = "with recurso as r: pasar fin"
```

y después exigía:

```python
assert TipoToken.WITH in tipos
assert TipoToken.AS in tipos
```

El lexer podía completar el análisis porque `with` y `as`, al no ser palabras
reservadas del lexer principal, coincidían con la regla general de
`IDENTIFICADOR`. El fallo ocurría después, al evaluar la primera aserción:
Python intentaba resolver `TipoToken.WITH`, miembro inexistente del enum, y
producía `AttributeError`. En una ejecución normal no se llegaba a evaluar
`TipoToken.AS`, aunque esa referencia era igualmente inválida.

Por tanto, el fallo no demostraba que el lexer hubiese tokenizado
incorrectamente una palabra reservada soportada; demostraba que el test
presuponía dos miembros que no formaban parte de `TipoToken`.

## 4. Estado del enum

La inspección de `TipoToken` en la base, el head y el merge confirma el mismo
contrato en las tres revisiones:

- existe `TipoToken.CON`;
- existe `TipoToken.COMO`;
- no existe `TipoToken.WITH`;
- no existe `TipoToken.AS`.

La PR #3586 no alteró el enum. En consecuencia, `WITH` y `AS` no eran nombres
alternativos pendientes de implementación, sino expectativas obsoletas del
test.

## 5. Contrato del core lexer

El lexer principal, `src/pcobra/cobra/core/lexer.py`, contiene reglas explícitas
para:

```text
con  -> TipoToken.CON
como -> TipoToken.COMO
```

No contiene reglas de palabra reservada para `with` ni para `as`. Como la regla
de identificador admite esos lexemas, el comportamiento real del core es:

```text
with -> TipoToken.IDENTIFICADOR
as   -> TipoToken.IDENTIFICADOR
```

Esto es distinto de afirmar que el core acepta `with ... as ...` como sintaxis
de context manager: no lo acepta como tal, porque esos identificadores no
activan el despacho de una declaración `con`.

## 6. Contrato del parser

El mapa principal de declaraciones de `src/pcobra/cobra/core/parser.py`
despacha `TipoToken.CON` a `declaracion_con`. Esta función:

1. exige que el primer token sea `TipoToken.CON` y, en caso contrario, informa
   `Se esperaba 'con'`;
2. analiza la expresión de contexto;
3. acepta opcionalmente `TipoToken.COMO`;
4. tras `como`, exige un `TipoToken.IDENTIFICADOR` y, si falta, informa
   `Se esperaba un identificador luego de 'como'`;
5. exige los dos puntos y el cierre `fin` del bloque;
6. construye `NodoWith` con el contexto, alias, cuerpo y marca asincrónica.

También existe soporte para `asincronico con`: `declaracion_asincronico`
comprueba `TipoToken.CON` y delega en `declaracion_con(asincronico=True)`.

El parser no consulta ni necesita `TipoToken.WITH` o `TipoToken.AS`. Sí quedan
textos históricos en un docstring, en el mensaje
`Se esperaba 'func', 'para' o 'con/with' después de 'asincronico'` y en una
advertencia sobre combinaciones `with ... as`; esos textos no cambian el
despacho ni los tokens realmente consumidos y son residuos independientes,
fuera del alcance documental de esta tarea.

## 7. Sintaxis documentada

Se revisaron las dos fuentes requeridas separando sus funciones:

- `docs/LIBRO_PROGRAMACION_COBRA.md` es la fuente normativa general. Su nota de
  contrato para palabras clave exige mantener coherentes Lexer, Parser, AST,
  transpiladores, documentación y pruebas cuando se introduzca una palabra
  nueva. No documenta `WITH` o `AS` como miembros de `TipoToken` ni presenta
  `with ... as ...` como forma canónica de este bloque.
- `docs/especificacion_tecnica.md` documenta expresamente que el bloque `con`
  gestiona contextos y ofrece este ejemplo vigente:

```cobra
con archivo("datos.txt") como f:
    imprimir(f.leer())
fin
```

Así, la documentación aplicable coincide con el core en la pareja
`con ... como ...`. Esta evidencia documental no debe confundirse con tooling
adicional ni con comentarios o mensajes históricos internos.

## 8. Test antes de #3586

En `54b4dc6232833ccabd21682c3238732675be6e51`, las líneas relevantes del test
eran:

```python
def test_lexer_palabras_nuevas_en():
    codigo = "with recurso as r: pasar fin"
    tokens = Lexer(codigo).analizar_token()
    tipos = [t.tipo for t in tokens if t.tipo != TipoToken.EOF]
    assert TipoToken.WITH in tipos
    assert TipoToken.AS in tipos
```

El punto exacto del primer fallo era la resolución de `TipoToken.WITH` en la
primera aserción, no la llamada anterior a `Lexer(...).analizar_token()`.
`TipoToken.AS` habría fallado del mismo modo si se hubiera alcanzado la segunda
aserción. Por ello, el caso no acreditaba un defecto del lexer.

## 9. Test después de #3586

En el head y en el merge, el test usa el contrato real:

```python
codigo = "con recurso como r: pasar fin"
```

y comprueba:

```python
assert TipoToken.CON in tipos
assert TipoToken.COMO in tipos
```

La prueba focal actual terminó con `1 passed in 0.27s`.

## 10. PR #3586

El diff exacto entre base y head contiene un único archivo:
`tests/unit/test_nuevos_tokens.py`, con tres inserciones y tres eliminaciones.
La PR sustituyó:

- `with recurso as r` por `con recurso como r`;
- `TipoToken.WITH` por `TipoToken.CON`;
- `TipoToken.AS` por `TipoToken.COMO`.

No modificó Lexer, Parser, enum, AST, runtime, transpiladores, gramática,
documentación normativa, workflows, dependencias ni lockfiles. La corrección
fue exclusivamente una alineación de la prueba con el contrato ya existente.

## 11. Pruebas focales

Se ejecutaron, sin corregir ni alterar código, las verificaciones solicitadas:

1. `python -m pytest -q tests/unit/test_nuevos_tokens.py::test_lexer_palabras_nuevas_en`
   — `1 passed in 0.27s`.
2. `python -m pytest -q tests/test_lexer.py tests/test_parser.py tests/test_lexer_parser_contract.py`
   — `13 passed in 0.21s`.
3. `python -m pytest -q tests/unit/test_parser_del_global.py tests/unit/test_interpreter.py::test_with_limpia_contexto_y_memoria_en_retorno_temprano_de_funcion tests/unit/test_interpreter.py::test_with_limpia_contexto_y_memoria_si_hay_excepcion`
   — `14 passed in 1.15s`.

Los nodeids relacionados con context managers siguen existiendo con los
nombres citados; no fue necesario localizar equivalentes alternativos.

## 12. Runtime Stabilization Contract

La API pública de GitHub Actions registra **Runtime Stabilization Contract**
como `completed / success` para ambos commits:

- head `30394be5a2e670f5b3f00a02943a0a09ae8ff8f4`: run
  [35085804489](https://github.com/Alphonsus411/pCobra/actions/runs/35085804489);
- merge `58706c4ceb9c27b392e610505955fc647fbff4b5`: run
  [35086519056](https://github.com/Alphonsus411/pCobra/actions/runs/35086519056).

Esto no equivale a CI global verde. Para el head constan fallos independientes
en `Label PRs by branch`, `Lint`, `tests`, `CI` y `CodeQL`; para el merge constan
fallos independientes en `Lint`, `CI`, `tests`, `Build & Release CLI Binaries`,
`Deploy Docs` y `CodeQL`. No se investigan ni se atribuyen esos resultados a
Task 10.

## 13. Causa raíz

La causa raíz fue una expectativa de test desfasada respecto del contrato
vigente. El test mezclaba la ortografía de Python (`with ... as ...`) con
nombres de enum inexistentes, mientras el enum, el lexer principal y el parser
ya estaban alineados en `CON/COMO`. No había una ausencia funcional que
requiriera añadir tokens o aliases.

## 14. Clasificación final

**EXPECTATIVA DE TEST OBSOLETA — CERRADO**

La clasificación queda sustentada porque `WITH` y `AS` no pertenecen al enum,
`CON` y `COMO` sí pertenecen, el core lexer/parser trabaja con `CON/COMO`, la
sintaxis documentada aplicable usa `con ... como ...` y #3586 sólo corrigió la
prueba. No fue necesario modificar producción.

## 15. Diferencia REPL vs core fuera de alcance

El lexer específico del REPL, `src/pcobra/cobra/cli/repl/cobra_lexer.py`, tiene
dos reglas que producen `TipoToken.CON`: una para `con` y otra para `with`. El
lexer principal no reproduce ese alias: allí `with` cae en
`TipoToken.IDENTIFICADOR`.

Esta diferencia entre tooling del REPL y core es un hallazgo independiente. No
se investiga ni se corrige en Task 10, no demuestra la existencia de
`TipoToken.WITH` y no justifica reabrir `WITH` como miembro del enum. Si se
considera necesario armonizar ambos componentes, deberá hacerse en una tarea
posterior con alcance propio.

## 16. Riesgos residuales

- Los textos históricos del parser que mencionan `with`, `as` o una mezcla de
  aliases pueden inducir a error, aunque no amplían el contrato efectivo.
- La divergencia del lexer del REPL puede hacer que una entrada se coloree o
  clasifique de manera distinta de como la acepta el core.
- Los fallos de otros workflows de Actions permanecen independientes; este
  informe no afirma que la CI global esté verde.
- No se evaluaron aliases ingleses, otros tokens históricos, identidad o
  `repr` del AST, `constant_folder`, `LarkParser`, Rust ni otros fallos de CI,
  porque están expresamente fuera del alcance.

Ninguno de estos riesgos cambia la conclusión forense de #3586 ni debe
resolverse dentro de esta microtarea.

## 17. Conclusión

`TipoToken.WITH` no pertenece al enum vigente y `TipoToken.AS` tampoco.
`TipoToken.CON` y `TipoToken.COMO` sí pertenecen al enum vigente. El parser
principal despacha y consume `CON/COMO`, y la sintaxis vigente documentada es
`con ... como ...`.

La PR #3586 corrigió una expectativa obsoleta del test para que comprobara el
contrato existente. No fue necesario modificar producción, y su diff confirma
que no se modificaron Lexer, Parser, enum, AST, runtime, transpiladores ni
documentación normativa. Por tanto, Task 10 puede cerrarse como:

**EXPECTATIVA DE TEST OBSOLETA — CERRADO**
