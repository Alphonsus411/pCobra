# Caché incremental de tokens y AST

Se ha incorporado un sistema de almacenamiento por fragmentos en
`backend/src/core/ast_cache.py`. Cada línea del código puede guardarse
por separado mediante un *checksum*, permitiendo reutilizar los
fragmentos que no cambian entre ejecuciones.

Para activarlo desde código se puede invocar `Lexer.tokenizar(incremental=True)`
y `ClassicParser.parsear(incremental=True)`, que consultarán la caché de
fragmentos antes de volver a analizar el texto.

La opción `--analysis` del comando `profile` muestra también las
estadísticas de tiempo del lexer y del parser usando `cProfile`.
