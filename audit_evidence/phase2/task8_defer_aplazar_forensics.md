# Phase 2 — Task 8: forense de DEFER/APLAZAR

## 1. SHA auditado

- Base auditada: `37f69139a21d5ef3c694e3b18282ee93ad05c950` (`work`).
- Fecha de la investigación: 2026-09-15 (UTC).
- El árbol estaba limpio al comenzar (`git status --short` no produjo salida).
- Esta investigación no modifica Lexer, Parser, AST, runtime, pruebas, documentación
  normativa, transpilers, workflows ni dependencias. El único cambio previsto es este
  informe.

## 2. Entorno

- Sistema: Linux `6.18.44`, `x86_64`.
- Python: `3.12.13`.
- pytest: `9.0.3`.
- Los comandos se ejecutaron desde `/workspace/pCobra` con el paquete del propio
  checkout.

## 3. Estado del enum

`TipoToken` está definido en `src/pcobra/cobra/core/lexer.py`.

- **`TipoToken.DEFER` no existe**. Tanto la inspección del enum como
  `hasattr(TipoToken, "DEFER")` dan resultado negativo.
- **`TipoToken.APLAZAR` sí existe**, y su valor es la cadena `"APLAZAR"`.
- No hay otro miembro del enum que represente esta sentencia ni un alias de enum
  para ella.

La sonda produjo literalmente:

```text
DEFER existe: False
APLAZAR existe: True
APLAZAR valor: APLAZAR
```

## 4. Contrato del lexer

La especificación vigente contiene una sola regla:

```python
(TipoToken.APLAZAR, re.compile(r"\b(defer|aplazar)\b"))
```

Por tanto, los dos lexemas son aliases textuales y convergen en la representación
interna canónica `TipoToken.APLAZAR`. La sonda temporal (no añadida al repositorio)
dio:

```text
defer [('APLAZAR', 'defer', 1, 1), ('EOF', None, 1, 6)]
aplazar [('APLAZAR', 'aplazar', 1, 1), ('EOF', None, 1, 8)]
```

Mapeo exacto:

| Lexema | Tipo producido | Valor conservado | Siguiente token |
|---|---|---|---|
| `defer` | `TipoToken.APLAZAR` | `"defer"` | `TipoToken.EOF` |
| `aplazar` | `TipoToken.APLAZAR` | `"aplazar"` | `TipoToken.EOF` |

## 5. Dispatch del parser

El constructor de `Parser` registra:

```python
TipoToken.APLAZAR: self.declaracion_defer,
```

`parsear()` recorre las declaraciones, `declaracion()` consulta
`self._factories` con el tipo del token actual y llama al handler encontrado. En
consecuencia, un token `APLAZAR` selecciona realmente `declaracion_defer`; esto
ocurre tanto en nivel superior como dentro del bucle que parsea el cuerpo de una
función.

Respuesta separada exigida:

- **A. Token que selecciona la función:** `TipoToken.APLAZAR`.
- **B. Token que la función intenta consumir:** `TipoToken.DEFER`.

## 6. Implementación de declaracion_defer

La implementación captura primero el token actual y acto seguido ejecuta:

```python
token_defer = self.token_actual()
self.comer(TipoToken.DEFER)
expresion = self.expresion()
```

Después debería construir `NodoDefer`. Si se encuentra fuera de función o método,
también debería registrar la advertencia:

```text
La instrucción 'defer' solo garantiza su ejecución dentro de una función o método [...].
```

Sin embargo, la evaluación de `TipoToken.DEFER` falla antes de llamar a `comer`,
antes de parsear la expresión, antes de crear el AST y antes de evaluar o registrar
la advertencia. Existe literalmente esta contradicción activa:

```text
dispatch: TipoToken.APLAZAR -> declaracion_defer
consumo:  self.comer(TipoToken.DEFER)  # miembro inexistente
```

## 7. Sintaxis normativa

La fuente normativa designada, `docs/LIBRO_PROGRAMACION_COBRA.md`, no contiene
ninguna aparición (sin distinguir mayúsculas) de `defer`, `aplazar` ni
`diferido/diferida`. Por ello, el libro vigente **no prescribe** actualmente
`aplazar expresión`, `defer expresión` ni ambas formas.

Documentación secundaria sí afirma que hay diferidos con `defer`/`aplazar`:
`docs/MANUAL_COBRA.md` y `docs/MANUAL_COBRA.rst`. Una propuesta histórica describe
`defer` como palabra reservada adicional, pero una propuesta no sustituye al libro
como contrato normativo. No se encontraron ejemplos Cobra actuales con ninguno de
los lexemas en `examples/`; los `defer` hallados en golden files son código Go de
salida, no sintaxis Cobra de entrada.

Separación contractual:

- **A. Sintaxis normativa:** no documentada en el libro vigente.
- **B. Aliases léxicos admitidos por producción:** `defer` y `aplazar`.
- **C. Representación interna canónica vigente:** `TipoToken.APLAZAR`.
- **D. Residuo:** `TipoToken.DEFER` en Parser y en una expectativa de test.

## 8. Alias textual defer/aplazar

Sí, ambos lexemas son aliases legítimos según la implementación vigente del Lexer,
la tabla contractual `tests/test_lexer_parser_contract.py` y los manuales
secundarios. No falta un alias textual: ambos se reconocen ya. Tampoco se necesita
que el nombre inglés implique un miembro `DEFER`; el modelo implementado es
precisamente:

```text
"defer"   -> TipoToken.APLAZAR
"aplazar" -> TipoToken.APLAZAR
```

## 9. Referencias a TipoToken.DEFER

La búsqueda de producción, pruebas, documentación y ejemplos encontró sólo estas
referencias relevantes en código vigente:

1. `src/pcobra/cobra/core/parser.py`: consumo imposible dentro de
   `declaracion_defer`.
2. `tests/unit/test_nuevos_tokens.py`: expectativa antigua
   `tipos.count(TipoToken.DEFER) == 2`, que falla durante la propia resolución del
   atributo.

También existen menciones documentales en auditorías (`CORE_AUDIT_PHASE1.md` y la
exclusión de alcance de Task 7); describen el hallazgo, no son consumidores.

La referencia del Parser no es código muerto: el dispatch la alcanza con cualquiera
de los dos lexemas.

## 10. Referencias a TipoToken.APLAZAR

Las referencias vigentes se clasifican así:

- **Enum:** declaración `APLAZAR = "APLAZAR"`.
- **Lexer:** regla conjunta para `defer|aplazar`.
- **Parser:** clave del dispatch hacia `declaracion_defer`.
- **Pruebas contractuales:** tanto `defer` como `aplazar` se esperan como
  `TipoToken.APLAZAR` en `tests/test_lexer_parser_contract.py`.
- **Documentación de auditoría:** informes anteriores registran la discrepancia.

No se hallaron referencias funcionales a `TipoToken.APLAZAR` en AST, runtime o
transpilers: esos estratos operan con `NodoDefer`, una vez construido.

## 11. Historial Git

Se ejecutaron las cuatro búsquedas solicitadas:

```text
git log -S'TipoToken.DEFER' --all --oneline --
git log -S'TipoToken.APLAZAR' --all --oneline --
git log -S'"defer"' --all --oneline --
git log -S'"aplazar"' --all --oneline --
```

Los resultados incluyen el snapshot raíz disponible `e3a08a4` y snapshots
posteriores grandes (`e8e050d`, `f70fb4f`), además de commits puramente
documentales de auditoría para las búsquedas de nombres de token. El repositorio
marca `e3a08a4` como commit *grafted*, sin padres accesibles. En ese snapshot más
antiguo disponible ya coexistían:

- enum `APLAZAR = "APLAZAR"`;
- Lexer `defer|aplazar -> APLAZAR`;
- dispatch `APLAZAR -> declaracion_defer`;
- consumo interno `TipoToken.DEFER`;
- test léxico que esperaba `TipoToken.DEFER`.

`git blame` atribuye las cuatro líneas de producción al mismo límite histórico
`e3a08a4`. Por tanto, el historial disponible **no demuestra que `DEFER` haya sido
jamás miembro del enum**, ni permite fechar una sustitución de `DEFER` por
`APLAZAR`. Sí demuestra que la inconsistencia ya estaba presente en la primera
instantánea auditable. Hablar de una migración/renombrado es una hipótesis plausible,
pero no probada; no se atribuye motivación.

## 12. Pruebas focales

Primero se buscaron nodeids mediante:

```text
python -m pytest --collect-only -q tests/unit/test_nuevos_tokens.py \
  tests/unit/test_parser_nuevos.py tests/test_lexer_parser_contract.py \
  tests/unit/test_to_python.py | rg 'defer|aplazar|lexer_reserved_words'
```

Luego se ejecutaron los cuatro casos que recorren Lexer, Parser dentro/fuera de
función y la integración Parser→transpiler Python:

```text
python -m pytest -q \
  tests/unit/test_nuevos_tokens.py::test_lexer_token_defer_y_aplazar \
  tests/unit/test_parser_nuevos.py::test_parser_defer_dentro_funcion \
  tests/unit/test_parser_nuevos.py::test_parser_defer_fuera_de_funcion_generar_advertencia \
  tests/unit/test_to_python.py::test_transpilador_python_parser_funcion_con_defer_importa_contextlib_y_exitstack
```

Resultado: **4 fallos**.

- El test léxico falla en `tests/unit/test_nuevos_tokens.py:47` con
  `AttributeError: type object 'TipoToken' has no attribute 'DEFER'`; el Lexer sí
  había producido los tokens, pero el test usa una expectativa obsoleta.
- Los otros tres fallan en `src/pcobra/cobra/core/parser.py:1116`, con la misma
  excepción. Los tracebacks muestran `declaracion()` → handler →
  `declaracion_defer`; por tanto, sí alcanzan Parser y la función problemática.
- Dentro de función, el traceback además muestra el bucle de
  `declaracion_funcion` (`parser.py:833`).
- Fuera de función no llega a producir la advertencia porque falla antes.
- La prueba Parser→transpiler no llega al transpiler porque no se construye AST.

La suite completa directamente relacionada con el parser se ejecutó como
`python -m pytest -q tests/unit/test_parser_nuevos.py`: **2 pasaron y 2 fallaron**;
los dos fallos son exactamente los casos defer dentro/fuera de función.

Las pruebas contractuales del Lexer:

```text
python -m pytest -q \
  tests/test_lexer_parser_contract.py::test_lexer_palabras_reservadas_con_cobertura_esperada \
  tests/test_lexer_parser_contract.py::test_lexer_no_tiene_especificaciones_reservadas_exactas_duplicadas
```

terminaron con **2 pasadas**, confirmando que el contrato actual espera ambos
lexemas como `APLAZAR` y que la regla no está duplicada.

Finalmente se construyeron nodos AST directamente para aislar estratos posteriores:
los casos defer de Python y JavaScript pasaron; el de Rust falló por texto adicional
de imports/preludio en la salida esperada. Ese fallo Rust no depende de Lexer,
Parser ni del nombre del token y queda expresamente fuera de esta auditoría. No se
encontró una suite de intérprete que consuma `NodoDefer`; la ruta real no podría
alcanzarla de todos modos porque se detiene en Parser.

## 13. Reproducción funcional

Se usó la forma no bloque documentada por la propia implementación
(`defer/aplazar` seguida de una expresión), sin persistir la sonda:

```text
defer imprimir("x")
aplazar imprimir("x")
```

Se envolvió temporalmente el handler ya registrado en la instancia para registrar
la entrada, sin modificar archivos. Resultado literal:

```text
'defer imprimir("x")': ENTRA declaracion_defer con APLAZAR
'defer imprimir("x")': AttributeError: type object 'TipoToken' has no attribute 'DEFER'
'aplazar imprimir("x")': ENTRA declaracion_defer con APLAZAR
'aplazar imprimir("x")': AttributeError: type object 'TipoToken' has no attribute 'DEFER'
```

Secuencia confirmada para ambas formas:

1. el Lexer tokeniza correctamente como `APLAZAR`;
2. el dispatch entra en `declaracion_defer`;
3. la evaluación de `TipoToken.DEFER` lanza `AttributeError`;
4. no se consume el token ni se parsea `imprimir("x")`;
5. no se construye `NodoDefer`;
6. no se alcanza runtime/transpiler ni la lógica de advertencias.

## 14. Causa raíz

La causa inmediata es una única referencia inválida en producción: el Lexer y el
dispatch usan el token canónico existente `APLAZAR`, mientras
`declaracion_defer()` intenta acceder al miembro inexistente `DEFER`. Es una
desalineación interna entre el token entregado por Lexer/dispatch y el consumido por
Parser, en una ruta pública y ejecutable para **ambos** aliases.

Hay además una expectativa obsoleta en un test léxico, pero no causa el defecto de
producción. La ausencia de documentación normativa impide afirmar qué ortografía
debería prescribir el lenguaje, pero no impide diagnosticar la contradicción entre
componentes: ambos lexemas ya convergen inequívocamente en `APLAZAR`.

## 15. Clasificación final

**D. DESALINEACIÓN LEXER/PARSER**

Es real, reproducible y tiene impacto funcional. No se clasifica como referencia
obsoleta sin impacto porque el dispatch la ejecuta; tampoco como alias ausente
porque ambos aliases existen. Aunque el patrón parece un posible renombrado
incompleto, el historial truncado no prueba una migración y la clasificación D es
la descripción específica demostrada por ejecución.

## 16. Riesgos residuales

- Toda sentencia Cobra que comience por `defer` o `aplazar` rompe en Parser con
  `AttributeError`, dentro y fuera de funciones.
- La advertencia fuera de ámbito funcional no puede emitirse.
- Las integraciones que parten de texto fuente no pueden alcanzar AST, intérprete o
  transpilers para esta característica.
- El test léxico antiguo puede confundir el diagnóstico al fallar por su propia
  referencia inexistente, aun cuando la tokenización sea correcta.
- El contrato no está recogido en el libro normativo; los aliases sólo están
  respaldados por producción, pruebas contractuales y manuales secundarios.
- La historia anterior a `e3a08a4` no está disponible en este checkout grafted, así
  que no puede resolverse forénsicamente si `DEFER` existió antes.
- El fallo independiente observado en el test Rust de un AST construido manualmente
  no debe mezclarse con esta reparación.

## 17. Reparación mínima recomendada

Para una futura Task 9, y **sin realizarla aquí**, la reparación mínima conceptual
es cambiar únicamente el consumo de `declaracion_defer` para que espere el token
canónico que realmente entrega el Lexer y activa el dispatch:
`TipoToken.DEFER` → `TipoToken.APLAZAR`. No se recomienda añadir `DEFER`, retirar
`APLAZAR` ni alterar los aliases léxicos.

La reparación debería ir acompañada, en un cambio separado, por:

1. actualizar la expectativa obsoleta del test léxico para comprobar dos tokens
   `TipoToken.APLAZAR` y conservar sus valores textuales `defer`/`aplazar`;
2. parametrizar pruebas de Parser con ambos lexemas, dentro de función, verificando
   `NodoDefer` y ausencia de advertencias;
3. parametrizar pruebas fuera de función, verificando `NodoDefer`, ubicación y la
   advertencia;
4. mantener una prueba de integración desde fuente hasta el consumidor posterior
   aplicable;
5. ejecutar primero esos nodeids y después las suites relacionadas;
6. decidir en una tarea documental independiente si el libro normativo debe definir
   la característica, sin cambiar documentación para ocultar el fallo.

Como la reparación requiere tocar Parser y un test, queda bloqueada por el alcance
explícito de Task 8 y debe recibir autorización específica en Task 9.
