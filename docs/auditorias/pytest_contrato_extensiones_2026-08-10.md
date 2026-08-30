# Auditoría de pytest del contrato de extensiones

Fecha: 2026-08-10  
Rama auditada: `work` (`f3daff95`)  
Base comparativa: `b3ce6c2fbbc566f69bfedc51eef75c0d0711d6db`

## Recolección y ejecución completa

- `pytest --collect-only -q`: **4934 pruebas recolectadas**.
- `pytest -q`: **4372 passed, 508 failed, 54 skipped, 0 xfailed y 3 errors**.
- No se usó `--maxfail`.

Los tres errores son errores de preparación de `tests/unit/test_token_cache.py`:
`sqlite3.OperationalError: no such table: ast_fragments`. Los errores de
preparación se informan además de las 4934 pruebas recolectadas, por lo que no
deben sumarse otra vez al total de pruebas.

## Familias observadas

Los 508 fallos y 3 errores se agruparon por su responsabilidad principal:

1. **Paridad REPL/script:** ejecución compartida, estado incremental y contrato
   de errores entre `run` y REPL.
2. **Filesystem safe mode:** metadatos de `usar "archivo"`, rutas permitidas y
   bloqueo de símbolos peligrosos.
3. **`usar`:** resolución de módulos, allowlist y superficie pública.
4. **Transpilación:** optimización del AST, backends oficiales, roundtrip y
   paridad de características.
5. **Identidad AST:** comparaciones de identificadores, consistencia de nodos y
   fixtures sintácticos.
6. **Packaging:** construcción de wheel, manifiestos y dependencias declaradas.
7. **Auditoría CLI:** carga de comandos, logging, políticas de targets y
   validación de dependencias.
8. **Otras:** caché SQLite, corelibs, sandbox, GUI y utilidades auxiliares.

## Reproducciones mínimas y comparación

Se creó el worktree temporal `/tmp/pCobra-b3ce6c2f` en el commit base. Cada
comando siguiente se ejecutó tanto en el árbol auditado como en dicho worktree,
con el mismo Python 3.12.13, pytest y dependencias instaladas:

| Familia | Nodo mínimo | Resultado en ambos árboles |
| --- | --- | --- |
| REPL/script | `tests/integration/test_run_repl_equivalence.py::test_misma_secuencia_semantica_equivale_entre_run_y_repl` | pasa aislado; el fallo completo depende del orden/estado de la suite |
| filesystem safe mode | `tests/unit/test_safe_mode.py::test_existe_no_se_habilita_solo_por_nombre_sin_usar_archivo` | mismo error de importación de `CliApplication` |
| `usar` | `tests/unit/test_usar.py::test_obtener_modulo_alias_cobra_usa_origen_oficial` | pasa aislado; el fallo completo depende del orden/estado de la suite |
| transpilación | `tests/unit/test_to_python.py::test_transpilador_condicional` | mismo `RuntimeError` de estructura AST inválida en `constant_folder` |
| identidad AST | `tests/unit/test_interpreter_identifier_comparisons.py::test_ast_directo_comparacion_identificador_sin_recursionerror` | mismo `TypeError` por `permitir_asignacion_inicial` |
| packaging | `tests/test_packaging_metadata.py::test_wheel_preserva_dependencias_obligatorias_de_pyproject` | mismo `CalledProcessError` de `python -m build` |
| auditoría CLI | `tests/unit/test_cli_logging.py::test_cli_no_debug` | mismo error de importación de `CliApplication` |
| otras/caché | `tests/unit/test_token_cache.py::test_obtener_tokens_reutiliza` | pasa aislado; el error completo depende del estado SQLite de la suite |

La ejecución completa en el worktree base produjo **4371 passed, 508 failed,
54 skipped, 0 xfailed y 3 errors**. Conservó los mismos 508 fallos y los mismos
tres errores de caché que el árbol auditado. La diferencia de una prueba pasada
corresponde a la prueba documental/de política añadida después del commit base.

Por tanto, todos los fallos observados son **preexistentes** conforme al criterio
de comparación solicitado. No se realizó ninguna corrección: los hallazgos
pertenecen a runtime, seguridad, Lexer/Parser, AST, packaging o transpiladores,
fuera del alcance permitido para cambios documentales o de configuración de
Black.

## Comprobaciones de alcance

- No se añadieron `skip` ni `xfail`, no se redujeron aserciones y no se
  introdujeron capturas genéricas.
- No se modificaron Lexer ni Parser durante esta auditoría.
- No fue necesario repetir la suite completa después de una corrección porque
  no hubo correcciones de código.
