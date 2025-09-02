# Caché incremental de tokens y AST

Se ha incorporado un sistema de almacenamiento por fragmentos en
`src/pcobra/core/ast_cache.py`. Cada línea del código puede guardarse
por separado mediante un *checksum*, permitiendo reutilizar los
fragmentos que no cambian entre ejecuciones.

Desde la versión 10.0.9, la caché de AST y tokens se almacena en
formato JSON en lugar de `pickle`, lo que reduce la superficie de
ataque al eliminar la deserialización insegura de datos.

El directorio utilizado para la caché puede modificarse mediante la
variable de entorno `COBRA_AST_CACHE`.

Para activarlo desde código se puede invocar `Lexer.tokenizar(incremental=True)`
y `ClassicParser.parsear(incremental=True)`, que consultarán la caché de
fragmentos antes de volver a analizar el texto.

```python
from cobra.core import Lexer, ClassicParser
```

Para perfilar estas fases desde la línea de comandos se puede ejecutar:

```bash
cobra profile programa.cobra --analysis
```

La opción `--analysis` del comando `profile` muestra también las
estadísticas de tiempo del lexer y del parser usando `cProfile`.
