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
| `como` | `COMO` | U:`PALABRAS_RESERVADAS` | L:`COMO` | P:`declaracion_con`/`declaracion_desde` | A:campo `alias` de `NodoWith`/`NodoImportDesde` | Py:`visit_with`/`visit_import_desde` | JS: mismos visitantes | Rs: mismos visitantes | T:`test_parser_del_global.py::test_parser_con_alias` | Libro:§3.6 | `as` figura en registro pero no es sintaxis | **PARCIAL** — cobertura dirigida no alcanza los tres backends |
| `con` | `CON` | U:`PALABRAS_RESERVADAS` | L:`CON` | P:`declaracion_con` | A:`NodoWith` | Py:`visit_with` | JS:`visit_with` | Rs:`visit_with` | T:`test_parser_del_global.py::test_parser_con_alias`, `test_to_python.py::test_transpilador_with_asincronico` | Libro:índice/§3.8 | `with` no es reconocido | **PARCIAL** — semántica JS/Rust es aproximada/comentada |
| `continuar` | `CONTINUAR` | U:`PALABRAS_RESERVADAS` | L:`CONTINUAR` | P:`declaracion_continuar` | A:`NodoContinuar` | Py:`visit_continuar` | JS:`visit_continuar` | Rs:`visit_continuar` | T:suites de control/transpiladores | Libro:§4.4 | — | **COMPLETO** — ruta completa |
| `decorador` | `IDENTIFICADOR` (la sintaxis usa `@`→`DECORADOR`) | U:`PALABRAS_RESERVADAS` | L:`DECORADOR` solo para `@` | P:`declaracion_decorador` consume `@` | A:`NodoDecorador` | Py:`visit_decorador` | JS:`visit_decorador` | Rs:`visit_decorador` | T:`test_parser_decorador.py` y pruebas de transpiladores | Libro:§3.10 publica `@` | — | **NO IMPLEMENTADO** — la palabra constante no puede encabezar la construcción |
| `defer` | `APLAZAR` | U:`PALABRAS_RESERVADAS` | L:`APLAZAR` | P:`declaracion_defer` intenta `TipoToken.DEFER` inexistente | A:`NodoDefer` | Py:`visit_defer` | JS:`visit_defer` | Rs:`visit_defer` | T:`test_parser_nuevos.py::test_parser_defer_dentro_funcion` evidencia la ruta | Libro: no lo documenta | `aplazar` | **INCONSISTENTE** — consumo imposible con el enum vigente |
| `desde` | `DESDE` | U:`PALABRAS_RESERVADAS` | L:`DESDE` | P:`declaracion_desde` | A:`NodoImportDesde` | Py:`visit_import_desde` | JS:`visit_import_desde` | Rs:`visit_import_desde` | T:`test_parser_errors_extra.py::test_desde_without_import`; transpiladores parciales | Libro:índice léxico/§3.6 | — | **PARCIAL** — falta prueba positiva integral por backend |
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

# 9. Caracterización de sintaxis `usar`

El Libro §3.6 limita la norma a `usar CADENA`, con nombre simple o ruta lógica
punteada dentro de la cadena. El Parser conserva además una rama compatible
para dos o más identificadores separados por puntos; rechaza un identificador
simple sin comillas. Todas las formas aceptadas producen
`NodoUsar(modulo: str)` sin ampliar por ello la gramática pública.

# 10. Flujo runtime y backends

El intérprete resuelve `NodoUsar` mediante `usar_modulo`, incorpora exports
saneados al ámbito plano y registra metadata validada por las políticas de
`usar`. Desde el mismo AST, `PythonAdapter` materializa la llamada runtime;
`JavaScriptAdapter` y `RustAdapter` emiten `// usar <modulo>`, un marcador
sintácticamente válido que no simula materialización runtime. La declaración
JavaScript de `imports_corelibs` queda sincronizada con su visitante real.

# 12. Resultado y evidencia

La regresión cubre desde fuente Cobra las cadenas simple y punteada, la ruta
punteada sin comillas aceptada por compatibilidad y el rechazo del identificador
simple sin comillas. También valida Python con `ast.parse`, JavaScript con
`node --check` y Rust con `rustc` cuando las herramientas están disponibles.
