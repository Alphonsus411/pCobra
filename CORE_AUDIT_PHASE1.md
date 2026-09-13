# Auditoría del core — Fase 1

# 1. Alcance y método

Esta fase fija una línea base reproducible del repositorio sin corregir
hallazgos. No se modificaron producción, Lexer, Parser, pruebas existentes,
ejemplos ni la documentación normativa. Las salidas completas se conservan en
`audit_evidence/phase1/`.

# 2. SHA auditado

- **SHA:** `21ff2307a1fa027156b2b4657c6baef7bfdc1a83`.
- **Rama y estado inicial:** `## work`, sin cambios listados por
  `git status --short --branch`.
- **Python:** `Python 3.12.13`.
- **Plataforma reportada por Python:**
  `Linux-6.18.44-x86_64-with-glibc2.39`.
- Estos datos se capturaron antes de modificar cualquier archivo.

# 3. Baseline

## 3.1 Comando oficial y variantes encontradas

El comando oficial anunciado por `Makefile` es `make test`. Su target ejecuta,
en este orden:

1. `python scripts/grammar_coverage.py --threshold=30` (el umbral se puede
   variar con `GRAMMAR_COV`).
2. `pytest --cov=src/pcobra tests --cov-report=term-missing --cov-fail-under=90`.

Variantes presentes en el repositorio:

- `make coverage`: `coverage run -m pytest` y después `coverage html`.
- `bash scripts/test.sh [argumentos]`: antepone `$PWD/src:$PWD` a
  `PYTHONPATH` y delega en `pytest`. El archivo no tiene permiso de ejecución
  en este checkout, por lo que la forma documentada `./scripts/test.sh` falla.
- `PYTHONPATH=$PWD/src pytest` y `PYTHONPATH=$PWD/src pytest --cov`, descritos
  en `CONTRIBUTING.md`.
- El `README.md` también conserva variantes directas con umbral de cobertura
  95 %, `PYTHONPATH=$PWD pytest`, `pytest --cov=pcobra tests/`, suites
  específicas y `python scripts/check.py` para el pipeline ampliado. Por tanto,
  esas referencias no son idénticas al target vigente de `Makefile`.

La configuración común de pytest en `pyproject.toml` limita la búsqueda a
`tests`, nombres `test_*.py`, clases `Test*` y funciones `test_*`; activa
marcadores estrictos, traceback corto, captura `fd`, toda la captura y las diez
pruebas más lentas.

## 3.2 Colección previa

Comando efectivo: `bash scripts/test.sh --collect-only`.

- **Collected:** 4977 items.
- **Passed / failed / xfailed / xpassed:** no aplican a `--collect-only` (no se
  ejecutaron casos).
- **Skipped durante colección:** 3.
- **Warnings:** 3.
- **Duración:** 14.90 s.
- **Errores de colección:** 0.
- **Código de salida:** 0.

Incidencia previa: el primer intento literal, `./scripts/test.sh
--collect-only`, terminó con código 126 y `Permission denied`; no llegó a
invocar pytest. La evidencia íntegra de la colección efectiva está en
`audit_evidence/phase1/pytest-collection.log`.

## 3.3 Suite oficial completa

`make test` **no llegó a ejecutar pytest**: el primer paso informó cobertura de
gramática **0.00 % (0/42)**, inferior al umbral **30.00 %**, y `make` terminó
con código 2. En consecuencia, para esa invocación oficial:

- **Passed / failed / skipped / xfailed / xpassed / warnings de pytest:** no
  disponibles, porque pytest no arrancó.
- **Errores de colección:** no aplican.
- **Duración de pytest:** no aplica.

La salida completa está en `audit_evidence/phase1/make-test.log`.

La segunda orden exacta del target se ejecutó aisladamente para diagnosticar el
bloqueo. Pytest terminó con código 4 antes de colección porque el entorno no
reconoce `--cov`, `--cov-report` ni `--cov-fail-under` (plugin `pytest-cov` no
disponible). Su salida se conserva en
`audit_evidence/phase1/pytest-official-command.log`.

Como observación adicional se lanzó la variante sin cobertura
`bash scripts/test.sh`. Recopiló 4977 items con 3 omisiones, alcanzó el 22 % y
quedó bloqueada al comenzar `tests/test_interactive_cmd_no_console.py`; se
interrumpió manualmente y terminó con código 1. Al no emitir resumen final,
**no es posible registrar cifras exactas** de passed, failed, skipped, xfailed,
xpassed, warnings o duración para esa ejecución, y no se infieren cifras a
partir de los puntos de progreso. La salida completa disponible está en
`audit_evidence/phase1/pytest-full-interrupted.log`.

Todos estos fallos se observaron sobre el SHA inicial, antes de crear este
informe; se registran expresamente como **fallos previos del baseline** y no
como regresiones introducidas por la auditoría.

# 4. Arquitectura relevante encontrada

- El proyecto usa layout `src`; el paquete principal es `src/pcobra` y las
  pruebas se concentran en `tests`.
- La entrada de consola `cobra` declarada en `pyproject.toml` apunta a
  `pcobra.cli:main`; esta fachada coordina la CLI pública.
- La implementación principal se organiza bajo `src/pcobra/cobra`, con capas
  separadas para CLI, pipeline de ejecución, core, backends, transpiladores,
  imports, configuración, GUI, QA y contratos de biblioteca estándar.
- También existen superficies en `src/pcobra/core`, `src/pcobra/corelibs` y
  `src/pcobra/standard_library`, además de integraciones GUI, LSP y Jupyter.
- Los Lexer y Parser canónicos inspeccionados están en
  `src/pcobra/cobra/core/lexer.py` y `src/pcobra/cobra/core/parser.py`. Quedan
  explícitamente fuera del alcance de modificación de esta fase.
- El contrato normativo de sintaxis y comportamiento continúa siendo
  `docs/LIBRO_PROGRAMACION_COBRA.md`.
- La validación oficial no es una única invocación de pytest: `make test`
  antepone un gate de cobertura gramatical, mientras que `make check` agrega
  smoke tests, lint, tipos y validación del contrato de runtime.

# 5. Matriz de palabras reservadas y construcciones

## 5.1 Método y leyenda

La fuente normativa usada para decidir si una forma pertenece a la superficie
pública es `docs/LIBRO_PROGRAMACION_COBRA.md`. El inventario de partida es el
`frozenset` `PALABRAS_RESERVADAS` de `src/pcobra/cobra/core/utils.py`; por eso
la tabla contiene sus **61 entradas exactas**, incluso cuando una entrada no
puede formar una construcción válida. Para cada una se comprobó, en este
orden, el patrón de `Lexer._inicializar_especificaciones`, el consumo efectivo
en `ClassicParser`, el nodo de `src/pcobra/core/ast_nodes.py`, los visitantes
de los tres backends y las suites solicitadas. Una coincidencia textual en una
prueba no se tomó como cobertura si la prueba no recorre la construcción.

Abreviaturas de archivo usadas en las celdas: **U** = `src/pcobra/cobra/core/utils.py`;
**L** = `src/pcobra/cobra/core/lexer.py`; **P** =
`src/pcobra/cobra/core/parser.py`; **A** = `src/pcobra/core/ast_nodes.py`;
**Py**, **JS** y **Rs** = `src/pcobra/cobra/transpilers/transpiler/to_python.py`,
`to_js.py` y `to_rust.py`; **T** = `tests/`. «Estructural» significa que el
token es consumido para delimitar o modificar otra construcción y no genera
un nodo independiente. Los estados de esta matriz se limitan deliberadamente
a `COMPLETO`, `PARCIAL`, `INCONSISTENTE`, `SIN TEST`, `SIN DOCUMENTAR` y
`NO IMPLEMENTADO`.

## 5.2 Trazabilidad

| Palabra Cobra | Token | Definición | Lexer | Parser | AST | Python | JavaScript | Rust | Tests | Documentación | Alias | Estado |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `afirmar` | `AFIRMAR` | U:`PALABRAS_RESERVADAS` | L:`AFIRMAR` | P:`declaracion_afirmar` | A:`NodoAssert` | Py:`visit_assert` | JS:`visit_assert` | Rs:`visit_assert` | T:`test_parser_nuevos.py::test_parser_afirmar`, `test_to_python_nuevos.py::test_transpilar_afirmar` | Libro:`afirmar` | — | **PARCIAL** — no hay prueba dirigida JS/Rust |
| `aplazar` | `APLAZAR` | U:`PALABRAS_RESERVADAS` | L:`APLAZAR` | P:`declaracion_defer` intenta `TipoToken.DEFER` inexistente | A:`NodoDefer` | Py:`visit_defer` | JS:`visit_defer` | Rs:`visit_defer` | T:`test_parser_nuevos.py::test_parser_defer_dentro_funcion` | Libro: sin `aplazar` | `defer` | **INCONSISTENTE** — token producido y token consumido difieren |
| `as` | `IDENTIFICADOR` | U:`PALABRAS_RESERVADAS` | L:`IDENTIFICADOR` | P: ningún consumo válido de `as` | A: sin nodo | Py: sin ruta fuente | JS: sin ruta fuente | Rs: sin ruta fuente | T: sin prueba Cobra dirigida | Libro: no lo publica | `como` es la forma implementada | **NO IMPLEMENTADO** — constante no utilizable en fuente Cobra |
| `asincronico` | `ASINCRONICO` | U:`PALABRAS_RESERVADAS` | L:`ASINCRONICO` | P:`declaracion_asincronico` | A:`NodoFuncion`/`NodoPara`/`NodoWith` | Py:`visit_funcion`/`visit_for`/`visit_with` | JS: mismos visitantes | Rs:`visit_funcion`/`visit_with`; sin `visit_for` | T:`test_to_python.py::test_transpilador_para_asincronico`, `test_to_js.py::test_transpilador_para_asincronico_js` | Libro:§3.8 | — | **PARCIAL** — ruta `para` sin backend Rust |
| `atributo` | `ATRIBUTO` | U:`PALABRAS_RESERVADAS` | L:`ATRIBUTO` | P:`exp_atributo`/`declaracion_asignacion` | A:`NodoAtributo` | Py:`visit_atributo` | JS:`visit_atributo` | Rs:`obtener_valor(NodoAtributo)` | T:`test_lexer_metodo_atributo.py::test_lexer_metodo_atributo_tokens`, `test_to_python_objects.py` | Libro:índice léxico | — | **COMPLETO** — recorrido disponible en los tres backends |
| `capturar` | `CAPTURAR` | U:`PALABRAS_RESERVADAS` | L:`CAPTURAR` | P:`declaracion_try_catch`, bloqueado por `TipoToken.CATCH` inexistente | A:`NodoTryCatch` | Py:`visit_try_catch` | JS:`visit_try_catch` | Rs:`visit_try_catch` | T:`test_to_python_extras.py::test_transpilar_try_catch_throw` solo prueba AST manual | Libro:§3.7 | `catch` | **INCONSISTENTE** — el parser evalúa un miembro inexistente |
| `case` | `CASE` | U:`PALABRAS_RESERVADAS` | L:`CASE` | P:`declaracion_switch` | A:`NodoCase`/`NodoSwitch` | Py:`visit_switch` | JS:`visit_switch` | Rs:`visit_switch` | T:`test_parser_switch.py::test_parser_switch` y suites `test_to_*` | Libro:§3.12 | `caso` | **COMPLETO** — alias comparte token y construcción |
| `caso` | `CASE` | U:`PALABRAS_RESERVADAS` | L:`CASE` | P:`declaracion_switch` | A:`NodoCase`/`NodoSwitch` | Py:`visit_switch` | JS:`visit_switch` | Rs:`visit_switch` | T:`test_parser_switch.py` cubre la construcción; sin prueba aislada del alias | Libro:§3.12 | `case` | **PARCIAL** — alias sin prueba dirigida propia |
| `catch` | `CAPTURAR` | U:`PALABRAS_RESERVADAS` | L:`CAPTURAR` | P:`declaracion_try_catch`, bloqueado por `TipoToken.CATCH` inexistente | A:`NodoTryCatch` | Py:`visit_try_catch` | JS:`visit_try_catch` | Rs:`visit_try_catch` | T:`test_to_python_extras.py::test_transpilar_try_catch_throw` solo AST manual | Libro:§3.7 | `capturar` | **INCONSISTENTE** — token legado referenciado no existe |
| `clase` | `CLASE` | U:`PALABRAS_RESERVADAS` | L:`CLASE` | P:`declaracion_clase` | A:`NodoClase` | Py:`visit_clase` | JS:`visit_clase` | Rs:`visit_clase` | T:`test_parser_clase.py::test_parser_declaracion_clase`, suites `test_to_*` | Libro:§3.5 | `estructura`, `registro` | **COMPLETO** — forma canónica trazada extremo a extremo |
| `como` | `COMO` | U:`PALABRAS_RESERVADAS` | L:`COMO` | P:`declaracion_con`/`declaracion_desde` | A:campo `alias` de `NodoWith`/`NodoImportDesde` | Py:`visit_with`/`visit_import_desde` | JS: mismos visitantes | Rs: mismos visitantes | T:`test_parser_del_global.py::test_parser_con_alias`, `test_desde_usar_auditoria.py` caracteriza la rama no pública | Libro:§3.6 no documenta alias para importación | `as` figura en registro pero no es sintaxis | **BLOQUEADO** — `como` solo es alcanzable en `NodoImportDesde` mediante `import`, no mediante `usar` |
| `con` | `CON` | U:`PALABRAS_RESERVADAS` | L:`CON` | P:`declaracion_con` | A:`NodoWith` | Py:`visit_with` | JS:`visit_with` | Rs:`visit_with` | T:`test_parser_del_global.py::test_parser_con_alias`, `test_to_python.py::test_transpilador_with_asincronico` | Libro:índice/§3.8 | `with` no es reconocido | **PARCIAL** — semántica JS/Rust es aproximada/comentada |
| `continuar` | `CONTINUAR` | U:`PALABRAS_RESERVADAS` | L:`CONTINUAR` | P:`declaracion_continuar` | A:`NodoContinuar` | Py:`visit_continuar` | JS:`visit_continuar` | Rs:`visit_continuar` | T:suites de control/transpiladores | Libro:§4.4 | — | **COMPLETO** — ruta completa |
| `decorador` | `IDENTIFICADOR` (la sintaxis usa `@`→`DECORADOR`) | U:`PALABRAS_RESERVADAS` | L:`DECORADOR` solo para `@` | P:`declaracion_decorador` consume `@` | A:`NodoDecorador` | Py:`visit_decorador` | JS:`visit_decorador` | Rs:`visit_decorador` | T:`test_parser_decorador.py` y pruebas de transpiladores | Libro:§3.10 publica `@` | — | **NO IMPLEMENTADO** — la palabra constante no puede encabezar la construcción |
| `defer` | `APLAZAR` | U:`PALABRAS_RESERVADAS` | L:`APLAZAR` | P:`declaracion_defer` intenta `TipoToken.DEFER` inexistente | A:`NodoDefer` | Py:`visit_defer` | JS:`visit_defer` | Rs:`visit_defer` | T:`test_parser_nuevos.py::test_parser_defer_dentro_funcion` evidencia la ruta | Libro: no lo documenta | `aplazar` | **INCONSISTENTE** — consumo imposible con el enum vigente |
| `desde` | `DESDE` | U:`PALABRAS_RESERVADAS` | L:`DESDE` | P:`declaracion_desde` exige `IMPORT` | A:`NodoImportDesde` solo por rama no normativa | Py:`visit_import_desde` | JS:`visit_import_desde` | Rs:`visit_import_desde` | T:`test_desde_usar_auditoria.py` parte de texto y cubre bloqueo y rama legada | Libro:solo índice léxico; §3.6 define únicamente `usar CADENA` | — | **BLOQUEADO** — `desde CADENA usar ...` tokeniza, pero no puede generar AST sin cambiar Parser y sin norma publicada |
| `eliminar` | `ELIMINAR` | U:`PALABRAS_RESERVADAS` | L:`ELIMINAR` | P:`declaracion_eliminar` | A:`NodoDel` | Py:`visit_del` | JS:`visit_del` | Rs:`visit_del` emite comentario | T:`test_parser_del_global.py::test_parser_del`/`test_transpilar_del` | Libro:índice léxico | — | **PARCIAL** — Rust no implementa semántica equivalente |
| `elseif` | `SINO_SI` | U:`PALABRAS_RESERVADAS` | L:`SINO_SI` | P:`_parse_sino_si` por tipo de token | A:`NodoCondicional` | Py:`visit_condicional` | JS:`visit_condicional` | Rs:`visit_condicional` | T:`test_lexer.py::test_lexer_sino_si_y_elseif_generan_token_unico` | Libro:compatibilidad léxica | `sino si` | **COMPLETO** — alias normalizado antes del parser |
| `enum` | `IDENTIFICADOR` | U:`PALABRAS_RESERVADAS` | L:`IDENTIFICADOR` | P:ningún consumo como declaración | A:sin nodo desde esa palabra | Py:sin ruta fuente | JS:sin ruta fuente | Rs:sin ruta fuente | T:`test_parser.py::test_parser_declaracion_enumeracion` usa `enumeracion` | Libro: no lo publica como sintaxis | `enumeracion` | **NO IMPLEMENTADO** — constante no utilizable en fuente Cobra |
| `enumeracion` | `ENUMERACION` | U:`PALABRAS_RESERVADAS` | L:`ENUMERACION` | P:`declaracion_enum` | A:`NodoEnum` | Py:`visit_enum` | JS:`visit_enum` | Rs:sin `visit_enum` | T:`test_parser.py::test_parser_declaracion_enumeracion`; Python/JS | Libro:índice léxico | `enum` no es reconocido | **PARCIAL** — falta tratamiento Rust |
| `esperar` | `ESPERAR` | U:`PALABRAS_RESERVADAS` | L:`ESPERAR` | P:`declaracion_esperar`/`exp_unario` | A:`NodoEsperar` | Py:`visit_esperar` | JS:`visit_esperar` | Rs:`visit_esperar` | T:`test_to_python.py::test_transpilador_corutina_await`, `test_to_js.py::test_async_function_and_await` | Libro:§3.8 | — | **PARCIAL** — falta prueba dirigida Rust |
| `estructura` | `ESTRUCTURA` | U:`PALABRAS_RESERVADAS` | L:`ESTRUCTURA` | P:`declaracion_clase` | A:`NodoClase` | Py:`visit_clase` | JS:`visit_clase` | Rs:`visit_clase` | T:`test_parser_clase.py::test_parser_declaracion_estructura` | Libro:índice léxico | `clase`, `registro` | **PARCIAL** — alias sin prueba integral de backends |
| `fin` | `FIN` | U:`PALABRAS_RESERVADAS` | L:`FIN` | P:`_exigir_fin` y consumidores de bloque | A:estructural, sin nodo propio | Py:estructural | JS:estructural | Rs:estructural | T:`test_parser_block_contract.py` | Libro:§3 sintaxis de bloques | — | **COMPLETO** — delimitador consumido antes del AST |
| `finalmente` | `FINALMENTE` | U:`PALABRAS_RESERVADAS` | L:`FINALMENTE` | P:`declaracion_try_catch`, inaccesible por referencias `TRY/CATCH` inexistentes | A:`NodoTryCatch.bloque_finally` | Py:`visit_try_catch` | JS:`visit_try_catch` | Rs:`visit_try_catch` | T:sin recorrido positivo fuente→AST | Libro:índice léxico | — | **INCONSISTENTE** — depende de una construcción rota |
| `func` | `FUNC` | U:`PALABRAS_RESERVADAS` | L:`FUNC` | P:`declaracion_funcion`/`declaracion_metodo` | A:`NodoFuncion`/`NodoMetodoAbstracto` | Py:`visit_funcion` | JS:`visit_funcion` | Rs:`visit_funcion` | T:`test_parser2.py::test_parser_funcion` y suites `test_to_*` | Libro:§3.4/§5 | `definir` solo existe en Lexer, fuera del registro | **COMPLETO** — forma canónica cubierta |
| `garantia` | `GARANTIA` | U:`PALABRAS_RESERVADAS` | L:`GARANTIA` | P:`declaracion_garantia` | A:`NodoGarantia` | Py:`visit_garantia` | JS:`visit_garantia` | Rs:sin `visit_garantia` | T:`tests/test_parser.py::test_parser_garantia_con_escape_terminador` | Libro:§3.7 | `guard` | **PARCIAL** — backend Rust no trata el nodo |
| `global` | `GLOBAL` | U:`PALABRAS_RESERVADAS` | L:`GLOBAL` | P:`declaracion_global` | A:`NodoGlobal` | Py:`visit_global` | JS:`visit_global` comentado | Rs:`visit_global` comentado | T:`test_parser_del_global.py::test_parser_global` | Libro:índice léxico | — | **PARCIAL** — JS/Rust preservan solo información textual |
| `graficar` | `GRAFICAR` | U:`PALABRAS_RESERVADAS` | L:`GRAFICAR` | P:`declaracion_graficar` | A:`NodoGraficar` | Py:`visit_graficar` | JS:`visit_graficar` | Rs:`visit_graficar` | T:suites Holobit y snapshots de backends | Libro:§3.3 | — | **COMPLETO** — ruta Holobit en tres backends |
| `guard` | `GARANTIA` | U:`PALABRAS_RESERVADAS` | L:`GARANTIA` | P:`declaracion_garantia` por token | A:`NodoGarantia` | Py:`visit_garantia` | JS:`visit_garantia` | Rs:sin `visit_garantia` | T:cobertura léxica dispersa; sin backend Rust | Libro:compatibilidad léxica | `garantia` | **PARCIAL** — alias hereda ausencia Rust |
| `hilo` | `HILO` | U:`PALABRAS_RESERVADAS` | L:`HILO` | P:`declaracion_hilo` | A:`NodoHilo` | Py:`visit_hilo` | JS:`visit_hilo` | Rs:sin `visit_hilo` | T:pruebas Python/JS; sin Rust dirigido | Libro:§3.8 | — | **PARCIAL** — falta backend Rust |
| `holobit` | `HOLOBIT` | U:`PALABRAS_RESERVADAS` | L:`HOLOBIT` | P:`declaracion_holobit`/`termino` | A:`NodoHolobit` | Py:`visit_holobit` | JS:`visit_holobit` | Rs:`visit_holobit` | T:`test_parser_holobit.py`, snapshots y `tests/integration/test_holobit_tiers.py` | Libro:§3.2/§6 | — | **COMPLETO** — cobertura multi-backend e integración |
| `import` | `IMPORT` | U:`PALABRAS_RESERVADAS` | L:`IMPORT` | P:`declaracion_import` y parte de `declaracion_desde` | A:`NodoImport`/`NodoImportDesde` | Py:`visit_import`/`visit_import_desde` | JS: mismos visitantes | Rs:visitantes comentado/`use` | T:`test_to_python_extras.py::test_transpilar_import`, integración CLI | Libro:§3.6/§7 | — | **PARCIAL** — Rust degrada import directo a comentario |
| `imprimir` | `IMPRIMIR` | U:`PALABRAS_RESERVADAS` | L:`IMPRIMIR` | P:`declaracion_imprimir` | A:`NodoImprimir` | Py:`visit_imprimir` | JS:`visit_imprimir` | Rs:`visit_imprimir` | T:`test_parser5.py::test_declaracion_imprimir`, integración cross-backend | Libro:§2.1/§3.3 | — | **COMPLETO** — construcción base extremo a extremo |
| `in` | `IDENTIFICADOR` | U:`PALABRAS_RESERVADAS` | L:`IDENTIFICADOR` | P:los bucles consumen `EN`, nunca `in` | A:sin nodo desde esa palabra | Py:sin ruta fuente | JS:sin ruta fuente | Rs:sin ruta fuente | T:sin prueba Cobra positiva | Libro: usa `en`, no `in` | `en` está implementado pero no en el registro | **NO IMPLEMENTADO** — constante no utilizable en fuente Cobra |
| `intentar` | `INTENTAR` | U:`PALABRAS_RESERVADAS` | L:`INTENTAR` | P:`declaracion_try_catch` referencia `TipoToken.TRY` inexistente | A:`NodoTryCatch` | Py:`visit_try_catch` | JS:`visit_try_catch` | Rs:`visit_try_catch` | T:solo AST manual en `test_to_python_extras.py` | Libro:§3.7 | `try` | **INCONSISTENTE** — parser falla antes de consumir el token válido |
| `interface` | `INTERFACE` | U:`PALABRAS_RESERVADAS` | L:`INTERFACE` | P:`declaracion_interface` | A:`NodoInterface`/`NodoMetodoAbstracto` | Py:`visit_interface` | JS:`visit_interface` | Rs:`visit_interface` | T:pruebas unitarias de interfaz/transpiladores | Libro: no la describe como construcción | `rasgo` solo en Lexer, fuera del registro | **SIN DOCUMENTAR** — implementación sin contrato normativo suficiente |
| `lambda` | `LAMBDA` | U:`PALABRAS_RESERVADAS` | L:`LAMBDA` | P:`termino` | A:`NodoLambda` | Py:`obtener_valor(NodoLambda)` | JS:`obtener_valor(NodoLambda)` | Rs:`obtener_valor(NodoLambda)` | T:`test_parser_nuevos.py::test_parser_lambda`, `test_to_python_nuevos.py::test_transpilar_lambda` | Libro:§3.2 | — | **PARCIAL** — no hay pruebas dirigidas JS/Rust |
| `lanzar` | `LANZAR` | U:`PALABRAS_RESERVADAS` | L:`LANZAR` | P:`declaracion_throw` referencia `TipoToken.THROW` inexistente | A:`NodoThrow` | Py:`visit_throw` | JS:`visit_throw` | Rs:`visit_throw` | T:transpiladores con AST manual | Libro:§3.7 | `throw` | **INCONSISTENTE** — miembro de token consumido inexistente |
| `macro` | `MACRO` | U:`PALABRAS_RESERVADAS` | L:`MACRO` | P:`declaracion_macro` | A:`NodoMacro` | Py:`expandir_macros` antes de visitar | JS:`expandir_macros` | Rs:`expandir_macros` | T:`test_parser_errors_extra.py` y pruebas de macros | Libro:§3.11 | — | **PARCIAL** — pruebas señaladas enfatizan parser, no los tres resultados |
| `metodo` | `METODO` | U:`PALABRAS_RESERVADAS` | L:`METODO` | P:`declaracion_metodo`, contextual en clase | A:`NodoMetodo` | Py:`visit_metodo` | JS:`visit_metodo` | Rs:`visit_metodo` | T:`test_lexer_metodo_atributo.py`, pruebas de objetos/backends | Libro:§3.5 | `func` también declara métodos | **COMPLETO** — consumo contextual y visitantes presentes |
| `mientras` | `MIENTRAS` | U:`PALABRAS_RESERVADAS` | L:`MIENTRAS` | P:`declaracion_mientras` | A:`NodoBucleMientras` | Py:`visit_bucle_mientras` | JS:`visit_bucle_mientras` | Rs:`visit_bucle_mientras` | T:`test_parser2.py::test_parser_bucle_mientras`, suites `test_to_*` | Libro:§4.2 | — | **COMPLETO** — ruta cubierta |
| `nolocal` | `NOLOCAL` | U:`PALABRAS_RESERVADAS` | L:`NOLOCAL` | P:`declaracion_nolocal` | A:`NodoNoLocal` | Py:`visit_nolocal` | JS:`visit_nolocal` comentado | Rs:`visit_nolocal` comentado | T:`test_parser_del_global.py::test_parser_nolocal` | Libro:índice léxico | — | **PARCIAL** — JS/Rust no reproducen semántica de ámbito |
| `option` | `OPCION` | U:`PALABRAS_RESERVADAS` | L:`OPCION` | P:`declaracion_option` | A:`NodoOption`/`NodoPattern` | Py:`visit_option` | JS:`visit_option` | Rs:`visit_option` | T:pruebas específicas de option/pattern en transpiladores | Libro:índice de sentencias | — | **COMPLETO** — declaración y valores opcionales tratados |
| `para` | `PARA` | U:`PALABRAS_RESERVADAS` | L:`PARA` | P:`declaracion_para` y comprensiones | A:`NodoPara`/`NodoListaComprehension`/`NodoDiccionarioComprehension` | Py:`visit_para` y comprehensions | JS:`visit_para` y comprehensions | Rs:sin `visit_para` ni comprehensions | T:`test_parser5.py::test_declaracion_para`, Python/JS | Libro:§4.3 | requiere `en` | **PARCIAL** — faltan rutas Rust |
| `pasar` | `PASAR` | U:`PALABRAS_RESERVADAS` | L:`PASAR` | P:`declaracion_pasar` | A:`NodoPasar` | Py:`visit_pasar` | JS:`visit_pasar` | Rs:`visit_pasar` | T:suites nuevas de parser/transpiladores | Libro:§3.3/§4.4 | — | **COMPLETO** — ruta completa |
| `proyectar` | `PROYECTAR` | U:`PALABRAS_RESERVADAS` | L:`PROYECTAR` | P:`declaracion_proyectar` | A:`NodoProyectar` | Py:`visit_proyectar` | JS:`visit_proyectar` | Rs:`visit_proyectar` | T:suites Holobit y snapshots | Libro:§3.3 | — | **COMPLETO** — ruta multi-backend |
| `registro` | `REGISTRO` | U:`PALABRAS_RESERVADAS` | L:`REGISTRO` | P:`declaracion_clase` | A:`NodoClase` | Py:`visit_clase` | JS:`visit_clase` | Rs:`visit_clase` | T:`test_parser_clase.py::test_parser_declaracion_registro` | Libro:índice léxico | `clase`, `estructura` | **PARCIAL** — alias sin prueba integral de backends |
| `retorno` | `RETORNO` | U:`PALABRAS_RESERVADAS` | L:`RETORNO` | P:`declaracion`/`declaracion_funcion` | A:`NodoRetorno` | Py:`visit_retorno` | JS:`visit_retorno` | Rs:`visit_retorno` | T:`test_parser4.py::test_parser_funcion_con_retorno`, suites `test_to_*` | Libro:§3.3/§5.1 | — | **COMPLETO** — ruta completa |
| `romper` | `ROMPER` | U:`PALABRAS_RESERVADAS` | L:`ROMPER` | P:`declaracion_romper` | A:`NodoRomper` | Py:`visit_romper` | JS:`visit_romper` | Rs:`visit_romper` | T:suites de control/transpiladores | Libro:§4.4 | — | **COMPLETO** — ruta completa |
| `segun` | `SWITCH` | U:`PALABRAS_RESERVADAS` | L:`SWITCH` | P:`declaracion_switch` | A:`NodoSwitch` | Py:`visit_switch` | JS:`visit_switch` | Rs:`visit_switch` | T:solo referencias léxicas; sin prueba dirigida del alias | Libro: no registra `segun` | `switch` | **SIN DOCUMENTAR** — alias ejecutable fuera del contrato normativo |
| `si` | `SI` | U:`PALABRAS_RESERVADAS` | L:`SI` | P:`declaracion_condicional`, guardas y comprensiones | A:`NodoCondicional`/`NodoGuard` | Py:`visit_condicional`/valor guard | JS:equivalentes | Rs:equivalentes | T:`tests/test_parser.py`, `test_parser_condicional_anidado.py`, backends | Libro:§4.1 | — | **COMPLETO** — construcción central cubierta |
| `sino` | `SINO` | U:`PALABRAS_RESERVADAS` | L:`SINO` | P:`declaracion_condicional`/`declaracion_garantia`/`declaracion_switch` | A:ramas de nodos correspondientes | Py:visitantes correspondientes | JS:visitantes correspondientes | Rs:`visit_condicional`/`visit_switch`; sin garantía | T:parser condicional y garantía | Libro:§4.1 | — | **PARCIAL** — rama de garantía carece de Rust |
| `sino si` | `SINO_SI` | U:`PALABRAS_RESERVADAS` | L:`SINO_SI` | P:`_parse_sino_si` | A:`NodoCondicional` anidado | Py:`visit_condicional` | JS:`visit_condicional` | Rs:`visit_condicional` | T:`test_lexer.py::test_lexer_sino_si_y_elseif_generan_token_unico`, `test_parser_condicional_anidado.py::test_parser_cascada_sino_si` | Libro:§4.1 | `elseif` | **COMPLETO** — forma canónica cubierta |
| `switch` | `SWITCH` | U:`PALABRAS_RESERVADAS` | L:`SWITCH` | P:`declaracion_switch` | A:`NodoSwitch`/`NodoCase`/`NodoPattern`/`NodoGuard` | Py:`visit_switch` | JS:`visit_switch` | Rs:`visit_switch` | T:`test_parser_switch.py`, pruebas `test_to_*::test_transpilador_switch` | Libro:§3.12 | `segun` | **COMPLETO** — forma documentada multi-backend |
| `throw` | `LANZAR` | U:`PALABRAS_RESERVADAS` | L:`LANZAR` | P:`declaracion_throw` referencia `TipoToken.THROW` inexistente | A:`NodoThrow` | Py:`visit_throw` | JS:`visit_throw` | Rs:`visit_throw` | T:solo AST manual en transpiladores | Libro:compatibilidad de errores | `lanzar` | **INCONSISTENTE** — el token producido no coincide con el comprobado |
| `transformar` | `TRANSFORMAR` | U:`PALABRAS_RESERVADAS` | L:`TRANSFORMAR` | P:`declaracion_transformar` | A:`NodoTransformar` | Py:`visit_transformar` | JS:`visit_transformar` | Rs:`visit_transformar` | T:suites Holobit y snapshots | Libro:§3.3 | — | **COMPLETO** — ruta multi-backend |
| `try` | `INTENTAR` | U:`PALABRAS_RESERVADAS` | L:`INTENTAR` | P:`declaracion_try_catch` referencia `TipoToken.TRY` inexistente | A:`NodoTryCatch` | Py:`visit_try_catch` | JS:`visit_try_catch` | Rs:`visit_try_catch` | T:solo AST manual en `test_to_python_extras.py` | Libro:compatibilidad de errores | `intentar` | **INCONSISTENTE** — el parser no puede iniciar la construcción |
| `usar` | `USAR` | U:`PALABRAS_RESERVADAS` | L:`USAR` | P:`declaracion_usar` | A:`NodoUsar` | Py:`visit_usar` | JS:`visit_usar` (marcador) | Rs:`visit_usar` (marcador) | T:integración `tests/integration/test_usar_*` y caracterización multi-backend | Libro:§3.6 y contrato REPL | — | **PARCIAL** — Python materializa; JS y Rust generan marcadores válidos sin materializar el runtime |
| `var` | `VAR` | U:`PALABRAS_RESERVADAS` | L:`VAR` | P:`declaracion_asignacion` | A:`NodoAsignacion` | Py:`visit_asignacion` | JS:`visit_asignacion` | Rs:`visit_asignacion` | T:`tests/test_lexer.py`, `tests/test_parser.py`, suites `test_to_*` | Libro:§2.2/§3.3 | — | **COMPLETO** — declaración canónica cubierta |
| `with` | `IDENTIFICADOR` | U:`PALABRAS_RESERVADAS` | L:`IDENTIFICADOR` | P:`declaracion_con` solo acepta `CON` | A:sin nodo desde esa palabra | Py:sin ruta fuente | JS:sin ruta fuente | Rs:sin ruta fuente | T:pruebas usan `con`; menciones `with` son Python | Libro: no lo publica | `con` | **NO IMPLEMENTADO** — constante no utilizable en fuente Cobra |
| `yield` | `GENERAR` | U:`PALABRAS_RESERVADAS` | L:`GENERAR` | P:`declaracion_yield` intenta `TipoToken.YIELD` inexistente | A:`NodoYield` | Py:`visit_yield` | JS:`visit_yield` | Rs:`visit_yield` | T:`test_to_js.py::test_transpilador_yield` usa AST manual | Libro:índice léxico | — | **INCONSISTENTE** — consumo imposible con el enum vigente |

## 5.3 Resultado del corte

Las entradas `as`, `decorador`, `enum`, `in` y `with` están en
`PALABRAS_RESERVADAS`, pero el Lexer las entrega como `IDENTIFICADOR` (o, para
decoradores, reconoce únicamente `@`) y el Parser no las consume como esas
palabras; conforme al criterio solicitado, **no forman parte de la superficie
pública válida**. Por separado, `try`/`intentar`, `catch`/`capturar`,
`throw`/`lanzar`, `defer`/`aplazar`, `finalmente` y `yield` llegan a tokens
específicos, pero sus funciones de parser consultan miembros `TipoToken`
inexistentes (`TRY`, `CATCH`, `THROW`, `DEFER`, `YIELD`), por lo que disponer
de nodo y visitante no hace ejecutable la sintaxis desde fuente. Este apartado
solo registra los hallazgos: no añade ni retira tokens, aliases o reglas.

# 6. Cambios y exclusiones

El corte inicial únicamente añadió este informe. La revisión incremental de
`usar` añade caracterización desde fuente, el visitante JavaScript mínimo y la
sincronización de `imports_corelibs` en la matriz. No modifica Lexer, Parser,
ejemplos ni documentación normativa.

La revisión incremental de `desde ... usar ...` añade exclusivamente una
regresión de caracterización y esta evidencia. No corrige producción: el Libro
no publica esa producción ni alias para ella y el Parser actual requiere
`IMPORT`. Conforme a las reglas de la auditoría, se detiene antes de modificar
Lexer o Parser; tampoco se presenta `import` como sintaxis pública Cobra.

# 7. Barrido acotado de palabras coincidentes con lenguajes backend

## 7.1 Alcance y criterio de clasificación

Se buscó cada palabra completa, respetando mayúsculas y minúsculas, en el
checkout versionado y se excluyeron `.git`, cachés y artefactos locales. El
análisis se acotó después a las superficies que permiten decidir el significado
de una coincidencia: Lexer y Parser canónicos, registro de palabras reservadas,
AST/runtime, transpiladores, ejemplos, documentación y pruebas. Cada aparición
se clasificó por su **contexto**, no solo por el archivo: **A** sintaxis pública,
**B** alias o rama histórica, **C** implementación interna del host, **D** texto
generado para un target, **E** nombre técnico/API (por ejemplo,
`visit_try_catch` o una capacidad llamada `async`), **F** documentación y **G**
prueba. Así, un `for` que itera una lista dentro del propio transpilador es C,
mientras que el `for` interpolado en su salida es D; una cadena Cobra dentro de
pytest sigue siendo G y aporta evidencia de A/B solo si recorre Lexer y Parser.

Para A y B se ejecutó la verificación desde texto fuente con
`Lexer(...).tokenizar()` y `ClassicParser(...).parsear()`. Los nombres que caen
en `IDENTIFICADOR` no se consideran palabras Cobra. Tampoco se consideraron
evidencia las palabras de Python que implementa el compilador ni las cadenas de
Python, JavaScript o Rust emitidas por los backends. La columna «backend»
resume exclusivamente D; `—` significa que no se encontró ese lexema como
palabra generada relevante, aunque pueda existir un visitante para el nodo.

## 7.2 Resultado

| término | español existente | público | alias | backend | decisión |
|---|---|---|---|---|---|
| `try` | `intentar` | No ejecutable: Lexer → `INTENTAR`; Parser falla al consultar `TipoToken.TRY` inexistente | **B**, histórico y documentado en el índice | **D:** Python `try`; JS `try` | Preservar; registrar la inconsistencia común con `intentar`, sin tocar Lexer/Parser |
| `catch` | `capturar` | No ejecutable: Lexer → `CAPTURAR`; Parser consulta `TipoToken.CATCH` inexistente | **B**, histórico y documentado en el índice | **D:** JS `catch`; Python usa `except` | Preservar; mismo riesgo de la construcción de errores |
| `throw` | `lanzar` | No ejecutable: Lexer → `LANZAR`; Parser consulta `TipoToken.THROW` inexistente | **B**, histórico y documentado en el índice | **D:** JS `throw`; Python usa `raise`; Rust degrada la operación | Preservar; no presentar el nodo o el backend como prueba de sintaxis válida |
| `switch` | `segun` | Sí: Lexer → `SWITCH` y Parser → `NodoSwitch`; el Libro lo incluye, pero no desarrolla una regla normativa propia | `segun` comparte token y es alias histórico no descrito por el Libro | **D:** JS `switch`; Python/Rust usan otras construcciones | Conservar ambas formas; recomendar completar el contrato normativo antes de elegir forma canónica |
| `case` | `caso` | Sí, contextual dentro de `switch`: Lexer → `CASE` y Parser → `NodoCase` | `caso` comparte token; ambas formas constan en el índice | **D:** JS `case`; Python/Rust usan otras construcciones | Conservar ambas formas; no inferir preferencia lingüística del nombre del nodo |
| `yield` | `generar` (nombre del token, no lexema español aceptado) | No ejecutable: Lexer → `GENERAR`; Parser consulta `TipoToken.YIELD` inexistente | **B**, legado documentado en el índice; no existe alias español equivalente en Lexer | **D:** Python/JS/Rust `yield` | Preservar y registrar el doble riesgo: Parser inconsistente y ausencia de forma española normativa |
| `for` | `para` | No: Lexer → `IDENTIFICADOR`; Parser solo consume `PARA` | No | **D:** Python/JS en el visitante del nodo; Rust solo en soporte generado, sin ruta `NodoPara` | Mantener como C/D/E donde corresponda; no convertirlo en alias Cobra |
| `in` | `en` | No: Lexer → `IDENTIFICADOR`; Parser consume `EN` | No, aunque figura en el registro y en el índice automático del Libro | **D:** Python/JS en bucles y comprensiones; Rust solo en soporte generado | Registrar conflicto del índice/registro con Lexer; no añadir sintaxis |
| `def` | `definir` | No: Lexer → `IDENTIFICADOR`; `TipoToken.DEF` no tiene patrón ni consumo | No; `definir` sí es alias de `func` | **D:** Python `def` | Clasificar coincidencias como C/D/E/F/G; no confundir el enum huérfano con sintaxis |
| `class` | `clase` | No: Lexer → `IDENTIFICADOR`; Parser consume `CLASE` | No | **D:** Python/JS `class`; Rust usa `struct` | No convertirlo en alias Cobra |
| `return` | `retorno` | No: Lexer → `IDENTIFICADOR`; Parser consume `RETORNO` | No | **D:** Python/JS/Rust `return` | No convertirlo en alias Cobra |
| `break` | `romper` | No: Lexer → `IDENTIFICADOR`; Parser consume `ROMPER` | No | **D:** Python/JS/Rust `break` | No convertirlo en alias Cobra |
| `continue` | `continuar` | No: Lexer → `IDENTIFICADOR`; Parser consume `CONTINUAR` | No | **D:** Python/JS/Rust `continue` | No convertirlo en alias Cobra |
| `while` | `mientras` | No: Lexer → `IDENTIFICADOR`; Parser consume `MIENTRAS` | No | **D:** Python/JS/Rust `while` | No convertirlo en alias Cobra |
| `async` | `asincronico` | No: Lexer → `IDENTIFICADOR`; Parser consume `ASINCRONICO` | No | **D:** Python/JS `async`; Rust `async` en salida compatible | Mantener como C/D/E; no convertirlo en alias Cobra |
| `await` | `esperar` | No: Lexer → `IDENTIFICADOR`; Parser consume `ESPERAR` | No | **D:** Python/JS `await`; Rust `.await` | No convertirlo en alias Cobra |
| `import` | `usar` (alternativa normativa, no alias token-a-token) | No normativa: Lexer → `IMPORT` y Parser → `NodoImport`, pero §3.6 publica `usar CADENA` | **B**, rama histórica; el índice automático contradice la prosa normativa | **D:** Python/JS `import`; Rust `use` o comentario | Preservar compatibilidad; mantenerla fuera de la superficie recomendada y registrar el conflicto documental |
| `from` | `desde` | No: Lexer → `IDENTIFICADOR`; Parser solo inicia la rama `DESDE` con `desde` | No | **D:** Python `from`; JS usa `from` en importaciones; Rust usa `use` | No confundir salida generada con sintaxis Cobra; permanece ligado al bloqueo de `desde` |
| `nonlocal` | `nolocal` | No: Lexer → `IDENTIFICADOR`; Parser consume `NOLOCAL` | No | **D:** Python `nonlocal`; JS/Rust emiten comentario | No convertirlo en alias Cobra |
| `global` | `global` | Sí: Lexer → `GLOBAL` y Parser → `NodoGlobal`; solo consta en el índice del Libro | No; es la forma existente | **D:** Python `global`; JS/Rust emiten comentario | Conservar; recomendar documentar semántica y diferencias backend |
| `lambda` | `lambda` | Sí, como expresión: Lexer → `LAMBDA` y Parser → `NodoLambda`; consta en el índice y valores permitidos | No; es la forma existente | **D:** Python `lambda`; JS/Rust usan cierres | Conservar sin traducir; no equiparar las formas generadas con la fuente |
| `func` | `definir` | Sí: ambos lexemas → `FUNC` y Parser → `NodoFuncion`; el Libro autoriza ambos | `definir` es alias público cubierto | **D:** Rust `fn`; Python `def`; JS `function` | Conservar `func` y `definir`; ninguna retirada normativa |
| `var` | `variable` | Sí: `VAR` acepta `=`; `VARIABLE` es una declaración distinta que exige `:=`; ambos llegan al manejador de asignación y constan en el Libro | No son aliases equivalentes: tienen tokens y operadores requeridos distintos | **D:** JS `let`; Rust `let`; Python asignación sin palabra | Conservar ambas formas y su semántica; no normalizar ni deprecar en esta fase |

Las coincidencias restantes del barrido quedan completamente explicadas por
C (control y declaraciones de Python/Rust que implementan el proyecto), D
(plantillas o resultados esperados de los tres targets), E (nombres de
visitantes, nodos, capacidades y APIs), F o G. En particular, los lexemas
ingleses hallados en `to_python.py`, `to_js.py`, `to_rust.py`, sus módulos de
nodos o snapshots no modifican la columna «público».

No se añaden pruebas en este corte. Los alias públicos conservados ya tienen
cobertura léxica en `tests/test_lexer_parser_contract.py`; `definir` tiene
además caracterización de Parser, `switch case` tiene pruebas
desde fuente y los aliases de excepciones/yield ya están caracterizados por el
contrato que expone su incoherencia. Añadir una prueba positiva de estos últimos
ocultaría que hoy no atraviesan el Parser canónico.

# 8. Auditoría incremental de clases y objetos

## 8.1 Método, alcance y contraste normativo

Este corte toma como norma exclusivamente el Libro §3.5 y parte de texto Cobra:
no cuenta como soporte que un test construya `NodoInstancia` o
`NodoLlamadaMetodo` a mano. Se siguió `Parser.declaracion_clase` hasta
`NodoClase`, el intérprete, `AnalizadorSemantico` y los generadores oficiales
`TranspiladorPython`, `TranspiladorJavaScript` y `TranspiladorRust`. También se
parseó `examples/clase_metodo_atributo.cobra` sin modificarlo.

El Libro solo formaliza `clase IDENTIFICADOR: bloque` y
`metodo IDENTIFICADOR([params]): bloque`; sus ejemplos añaden `atributo saldo`
y `self.nombre = nombre`, pero esas dos formas **no coinciden** con el Parser.
El ejemplo versionado sí usa las formas efectivas
`atributo self nombre = nombre` y `atributo self nombre`, y produce un
`NodoClase` con dos `NodoMetodo`. Esta aceptación no demuestra instanciación ni
llamada porque el archivo únicamente declara la clase.

Leyenda: **SOPORTADO** exige ruta pública desde fuente y comportamiento coherente;
**PARCIAL** conserva alguna parte útil pero no el contrato entero; **ROTO** es
una característica pretendida que tiene un reproductor desde fuente y falla;
**NO SOPORTADO** significa que ni el Libro ni el flujo efectivo publican la
característica. «Sin test fuente» distingue explícitamente las pruebas de AST
manual, que solo evidencian componentes internos.

## 8.2 Matriz por construcción

| Elemento | Sintaxis Cobra exacta contrastada | Nodo AST desde Parser | Ejecutor / generador | Evidencia de test | Estado |
|---|---|---|---|---|---|
| Clase mínima | `clase Vacia: fin` | `NodoClase("Vacia", [], [])` | `ejecutar_clase`; `visit_clase` Py/JS/Rust; semántico `visit_clase` | `test_parser_clase.py::test_parser_declaracion_clase` solo usa clase con método; sin test mínimo multi-backend | **ROTO**: runtime registra la clase y JS/Rust emiten estructura, pero Python genera `class Vacia:` sin `pass`, sintaxis inválida |
| Instanciación | `var c = C()` | `NodoAsignacion(..., NodoLlamadaFuncion("C", []))`, **no** `NodoInstancia` | runtime entra en `ejecutar_llamada_funcion`; backends emiten llamada ordinaria (`C()`, y no `new C()` en JS) | `test_interpreter_objects.py` y `test_to_python_objects.py` construyen `NodoInstancia` manualmente; sin test fuente | **ROTO**: el intérprete imprime `Función 'C' no implementada` y asigna `None`; `ejecutar_instancia` es inalcanzable desde esta sintaxis |
| Constructor | Declaración aceptada: `metodo __init__(self, nombre): ... fin` (también `inicializar`, normalizado a `__init__`); el Libro muestra `__init__(nombre)` | `NodoMetodo(nombre="__init__", ...)`; ninguna llamada crea `NodoInstancia` ni dispara el método | `_construir_clase` almacena el descriptor, pero `ejecutar_instancia` no busca constructor; visitantes de método lo emiten literalmente | `test_parser_clase.py::test_parser_clase_alias_choque_nombres` comprueba normalización, no construcción; sin test fuente de constructor | **ROTO**: se declara, pero ni la instanciación pública ni `ejecutar_instancia` lo ejecutan |
| Atributos de instancia | Forma efectiva: `atributo self nombre = nombre`; acceso: `atributo self nombre`. La forma del Libro `self.nombre = nombre` falla | `NodoAsignacion(NodoAtributo(...), ...)` / `NodoAtributo`; la forma punteada solo es expresión, no destino de asignación | `ejecutar_asignacion` escribe `__atributos__`; `evaluar_expresion` lee; `visit_atributo` Py/JS y `obtener_valor` Rust | el ejemplo fuente prueba parseo indirecto; `test_interpreter_objects.py::test_atributos_en_instancia` usa AST manual | **PARCIAL/ROTO público**: el cuerpo se representa y genera, pero no hay instancia pública sobre la que ejecutarlo; además el ejemplo normativo punteado no parsea |
| Atributos de clase | No hay sintaxis OO normativa. `var x = 1` dentro del bloque es admitido como sentencia genérica | `NodoAsignacion` guardado en el campo `NodoClase.metodos` | semántico lo visita; `_construir_clase` intenta tratarlo como función y falla; Python emite atributo, JS `let` dentro de clase y Rust `let` dentro de `impl` | sin test fuente dirigido | **ROTO**: `clase C: var x = 1 fin` causa `AttributeError` en runtime y salida inválida JS/Rust; no se eleva esa aceptación accidental a sintaxis documentada |
| Métodos | `metodo f(self, x): ... fin` (Parser admite también `func`) | `NodoMetodo` dentro de `NodoClase.metodos` | `_construir_funcion`; semántico `visit_metodo`; `visit_metodo` Py/JS/Rust | parser cubierto en `test_parser_clase.py`; paridad backend en `test_transpiler_feature_parity.py` usa AST manual | **PARCIAL**: declaración trazada, pero llamada pública rota; JS conserva `self` como argumento explícito y Rust emite parámetros sin tipos |
| Acceso | `atributo objeto nombre` y, solo como expresión, `objeto.nombre` | ambos producen `NodoAtributo` | lector runtime y `visit_atributo`/`obtener_valor` de tres backends | `test_to_python_objects.py` y runtime de objetos usan AST manual; ejemplo cubre la primera forma durante parseo | **PARCIAL**: el nodo es alcanzable, pero un objeto Cobra no puede obtenerse por instanciación pública |
| Modificación | `atributo objeto nombre = expresion`; no `objeto.nombre = expresion` | `NodoAsignacion` cuyo destino es `NodoAtributo` | `ejecutar_asignacion`; visitantes de asignación + atributo | ejemplo fuente contiene la forma efectiva; runtime dirigido solo con AST manual | **PARCIAL** por la misma ausencia de objetos instanciables desde fuente |
| Llamada de método | La forma natural `objeto.metodo(args)` no tiene producción efectiva | ninguna: `termino` reduce la cadena punteada a `NodoAtributo` y deja `(`; el reproductor termina en `ParserError` | existe `ejecutar_llamada_metodo` y visitantes Py/JS, pero no son alcanzables; Rust ni siquiera registra visitante de llamada | `test_interpreter_objects.py` y `test_to_python_objects.py` construyen `NodoLlamadaMetodo` manualmente | **ROTO** |
| Referencia propia | `self` es un `IDENTIFICADOR` ordinario y debe escribirse explícitamente en la lista si el cuerpo lo usa | `NodoIdentificador("self")`; no hay nodo propio | `ejecutar_llamada_metodo` inyecta `self`, pero solo en la ruta manual; backends lo imprimen sin normalización | pruebas manuales de objetos; ejemplo fuente solo declara cuerpos | **PARCIAL**: sin regla normativa autónoma, validación de posición ni llamada pública |
| Herencia simple | Forma efectiva no formalizada: `clase Derivada(Base): ... fin` | `NodoClase.bases == ["Base"]` | semántico valida base/ciclos; runtime resuelve y busca métodos en bases; Py emite `(Base)`, JS `extends Base`, Rust solo comentario | `test_semantico.py` y `test_interpreter_herencia.py` (este último con AST manual); sin prueba fuente extremo a extremo | **PARCIAL**: parseo/runtime interno existen, pero la llamada pública falla y Rust no implementa herencia |
| Superclase | No hay sintaxis `super` publicada ni producción/nodo específico | ninguno | ninguno | sin test Cobra fuente | **NO SOPORTADO** |
| Override | No tiene palabra especial: dos clases pueden declarar el mismo nombre mediante la sintaxis de herencia efectiva | dos `NodoMetodo` homónimos en clases distintas | runtime buscaría primero en derivada; backends emiten métodos, con las limitaciones anteriores | sin test fuente de override; herencia manual solo prueba método heredado | **PARCIAL**: resolución interna plausible y trazada, pero no invocable desde fuente; no se declara completa por capacidades del target |
| Métodos estáticos | No hay decorator/modificador normativo ni flujo efectivo específico | ninguno | ninguno | sin test Cobra fuente | **NO SOPORTADO** |
| Métodos de clase | No hay decorator/modificador normativo ni equivalente a `cls` | ninguno | ninguno | sin test Cobra fuente | **NO SOPORTADO** |
| Visibilidad | No hay `publico`/`privado`/`protegido` ni regla normativa; guion bajo es solo parte del identificador | ninguno | ninguno | sin test Cobra fuente | **NO SOPORTADO** |
| Composición | No posee sintaxis especial; requeriría guardar una instancia como atributo con las construcciones anteriores | sería `NodoAsignacion` + `NodoAtributo` + `NodoInstancia`, pero Parser nunca crea el último | componentes internos del runtime, sin ruta fuente completa | sin test fuente; no basta la capacidad de Python/JS | **ROTO** como programa OO público; no es una característica independiente implementada |
| Retorno de método | `retorno expresion` es la forma canónica del Libro (`retornar` es aceptada); dentro de método | `NodoRetorno` en `NodoMetodo.cuerpo` | `ejecutar_llamada_metodo` captura `_ControlRetorno`; `visit_retorno` en tres backends | tests de retorno general; pruebas manuales de métodos retornan valores | **PARCIAL**: funciona en la ruta interna manual, pero no mediante llamada desde fuente |
| Parámetros de método | lista `metodo f(self, x, y): ... fin`; son nombres sin tipos en esta ruta | `NodoMetodo.parametros: list[str]` | runtime omite el primer parámetro al ligar argumentos; visitantes los copian literalmente | parser comprueba nombre/método, pruebas manuales ejercitan un argumento | **PARCIAL**: no valida aridad en `ejecutar_llamada_metodo` y depende de una llamada inalcanzable |
| Objetos como argumentos o resultados | No hay sintaxis especial: serían identificadores en argumentos o `retorno obj` | identificadores/retorno sí; no hay `NodoInstancia` desde fuente ni `NodoLlamadaMetodo` para consumir/producir el objeto | descriptores internos pueden circular como valores, pero solo entrando por AST manual | sin test fuente extremo a extremo | **ROTO** por depender de instanciación y llamada rotas |

## 8.3 Reproductores mínimos observados

```cobra
# Instanciación: parsea como llamada de función y el runtime asigna None.
clase C:
fin
var c = C()
```

```cobra
# Llamada: ParserError en el paréntesis de cierre.
clase C:
    metodo f(self):
        retorno 1
    fin
fin
var c = C()
imprimir c.f()
```

```cobra
# Atributo de clase accidental: AttributeError en el runtime y JS/Rust inválidos.
clase C:
    var x = 1
fin
```

```cobra
# Las formas mostradas por §3.5 tampoco atraviesan el Parser actual.
clase Cuenta:
    atributo saldo
fin
```

La última forma falla con «Se esperaba el nombre del atributo»; la asignación
`self.nombre = nombre` del constructor del Libro falla al encontrar `=` porque
el Parser solo admite el destino prefijado `atributo self nombre`. Corregir
estas discrepancias exigiría decidir primero el contrato normativo y después
tocar Parser, ambas acciones fuera de este hallazgo documental.

# 9. Caracterización de sintaxis `usar`

El Libro §3.6 limita la norma a `usar CADENA`, con nombre simple o ruta lógica
punteada dentro de la cadena. El Parser conserva además una rama compatible
para dos o más identificadores separados por puntos; rechaza un identificador
simple sin comillas. Todas las formas aceptadas producen
`NodoUsar(modulo: str)` sin ampliar por ello la gramática pública.

Para la construcción solicitada, el Libro solo incluye `desde` en el índice de
palabras reservadas. No contiene regla, ejemplo ni contrato
`desde CADENA usar IDENTIFICADOR`, y §3.6 no documenta alias `como` para
importaciones. El Lexer produce correctamente `DESDE`, `CADENA`, `USAR`,
`IDENTIFICADOR`, `COMO`, `IDENTIFICADOR`; después `declaracion_desde` rechaza
`USAR` porque exige `IMPORT`. La rama existente con la palabra `import` crea
`NodoImportDesde(modulo, nombre, alias)`, pero queda caracterizada únicamente
como implementación legada no normativa.

# 10. Flujo runtime, semántico y backends de clases

`Parser.declaracion_clase` acepta bases entre paréntesis y cualquier declaración
en el cuerpo, aunque el campo resultante se llame `metodos`. Cada método se
normaliza mediante `ALIAS_METODOS_ESPECIALES` y se guarda como `NodoMetodo`.
No existe, en cambio, una transición del Parser hacia `NodoInstancia` o
`NodoLlamadaMetodo`: `C()` es `NodoLlamadaFuncion` y `obj.f()` se atasca después
de construir un `NodoAtributo`. Ese corte anterior al AST domina el estado de
instanciación y llamada.

`AnalizadorSemantico.visit_clase` declara la clase, valida que las bases ya sean
clases, detecta ciclos y visita el contenido en un ámbito nuevo. No valida que
el contenido sea realmente método, la posición de `self`, aridad de métodos,
constructores, override ni visibilidad. En runtime, `_construir_clase` presupone
que todo elemento tiene forma de función; por eso una asignación admitida dentro
de clase rompe. `ejecutar_instancia` crea el diccionario de atributos pero no
llama `__init__`. `ejecutar_llamada_metodo` implementa búsqueda derivada-primero,
inyecta `self` y propaga retornos, pero ambos ejecutores dependen de nodos que el
Parser no produce.

Python genera clases y métodos, pero omite `pass` en una clase vacía. JavaScript
usa solo la primera base, deja las adicionales en comentario y conserva `self`
como parámetro explícito. Rust representa siempre una estructura vacía, deja
las bases en comentario, copia firmas sin tipos y no tiene visitante registrado
para `NodoLlamadaMetodo`. Por tanto, la existencia de una construcción homóloga
en Python o JavaScript no se contabiliza como soporte Cobra.

# 12. Resultado y evidencia

La regresión cubre desde fuente Cobra las cadenas simple y punteada, la ruta
punteada sin comillas aceptada por compatibilidad y el rechazo del identificador
simple sin comillas. También valida Python con `ast.parse`, JavaScript con
`node --check` y Rust con `rustc` cuando las herramientas están disponibles.


La regresión específica `tests/unit/test_desde_usar_auditoria.py` demuestra
desde texto Cobra los tokens de `desde "paquete" usar simbolo como alias` y su
rechazo antes de Python, JavaScript y Rust. Además caracteriza, sin elevarla a
sintaxis pública, la rama legada `import`: comprueba el tipo y los tres campos
del nodo, las tres emisiones, `ast.parse`, `node --check` y `rustc` cuando las
herramientas están instaladas. No existe una prueba positiva normativa que se
pueda añadir honestamente mientras falte la producción en el Libro y el Parser.

# 14. Estado del hallazgo de clases y objetos

**ROTO.** La declaración aislada llega a `NodoClase`, pero ni siquiera la clase
mínima es portable porque Python genera un bloque vacío inválido. El corte
principal está en Parser: la sintaxis pública natural de construcción produce
`NodoLlamadaFuncion` en vez de `NodoInstancia`, y una llamada punteada no produce
`NodoLlamadaMetodo`. Constructor, atributos ejecutables, override, composición,
retornos de método y objetos como argumentos/resultados quedan aguas abajo de
esos dos bloqueos. Herencia simple es **PARCIAL** y `super`, estáticos, métodos
de clase y visibilidad son **NO SOPORTADO**, no pendientes de implementación en
este corte.

No se modifica Lexer ni Parser. Tampoco se corrigen ejemplos o el Libro para
ocultar que `atributo saldo` y `self.nombre = nombre` contradicen la forma que
acepta hoy el Parser. La solución requiere una decisión normativa explícita y
autorización específica para modificar Parser; por las reglas del repositorio,
la auditoría se detiene y documenta el bloqueo.

# 15. Criterio de cierre pendiente para clases

El hallazgo solo podrá cerrarse incrementalmente, uno por uno, cuando: (1) el
Libro defina sin contradicción clase vacía, construcción, llamada, constructor,
atributos y herencia; (2) exista autorización para los cambios de Parser que
sean imprescindibles; (3) pruebas desde **texto Cobra**, no AST manual,
comprueben los nodos públicos; (4) semántico e intérprete validen y ejecuten el
mismo contrato, incluido constructor, aridad, `self`, atributos y retorno; (5)
los tres targets generen sintaxis válida y semántica declarada; y (6) se decida
por separado si las características hoy **NO SOPORTADO** entrarán alguna vez en
la norma. Hasta entonces no debe usarse la capacidad OO del lenguaje anfitrión
como evidencia ni promocionarse `NodoInstancia`/`NodoLlamadaMetodo` manuales a
sintaxis pública.
