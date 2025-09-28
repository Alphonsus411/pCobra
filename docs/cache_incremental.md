# Caché incremental de tokens y AST

El módulo [`src/pcobra/core/ast_cache.py`](../src/pcobra/core/ast_cache.py)
centraliza la caché incremental utilizando **SQLitePlus** como backend. La
información se guarda en la base de datos `~/.cobra/sqliteplus/core.db` (ruta
predeterminada) y requiere la variable de entorno `SQLITE_DB_KEY` para iniciar la
conexión. Si necesitas mover la base, establece `COBRA_DB_PATH` antes de ejecutar
cualquier comando.

```bash
export SQLITE_DB_KEY="clave-local"
export COBRA_DB_PATH="$HOME/.cobra/sqliteplus/core.db"  # Opcional
```

La antigua variable `COBRA_AST_CACHE` sigue aceptándose como alias de
compatibilidad: al definirla, el sistema calcula automáticamente una ruta
`cache.db` dentro del directorio indicado y muestra una advertencia de
obsolescencia.

## Uso desde código

Las APIs continúan disponibles mediante `Lexer.tokenizar(incremental=True)` y
`ClassicParser.parsear(incremental=True)`. Ambos métodos consultan primero la
base de datos para recuperar el AST o los tokens asociados al hash del código y
solo ejecutan el análisis completo si no existe entrada previa.

```python
from cobra.core import Lexer, ClassicParser
```

## Limpieza y mantenimiento

La manera soportada de limpiar el almacenamiento es ejecutar el subcomando:

```bash
cobra cache --vacuum
```

El parámetro `--vacuum` recompac ta la base de datos tras borrar las entradas.

## Migración desde archivos JSON

Si conservas caches generadas con versiones anteriores (archivos `.ast` y `.tok`),
puedes importarlas ejecutando el script auxiliar incluido en `scripts/`:

```bash
python scripts/migrar_cache_sqliteplus.py --origen /ruta/a/tu/cache
```

Antes de lanzarlo configura `SQLITE_DB_KEY` (y `COBRA_DB_PATH` si quieres usar
una ubicación alternativa). El proceso recorre cada hash, crea los registros en
SQLite y deja la base lista para reutilizar los resultados en compilaciones
posteriores.

## Perfilado

Para perfilar las etapas de análisis léxico y sintáctico desde la línea de
comandos puedes ejecutar:

```bash
cobra profile programa.cobra --analysis
```

La opción `--analysis` del comando `profile` imprime estadísticas de tiempo
provenientes de `cProfile`, facilitando la inspección del impacto de la caché en
la ejecución.
