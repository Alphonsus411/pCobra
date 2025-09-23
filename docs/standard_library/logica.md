El módulo `standard_library.logica` reexpone las utilidades booleanas de
`pcobra.corelibs.logica` para que puedan usarse directamente desde programas de
alto nivel. Todas las funciones validan sus argumentos y mantienen la misma
semántica en los distintos backends soportados.

## `coalesce`

La función `coalesce` ayuda a escoger el primer valor válido de una lista de
candidatos, igual que `COALESCE` en SQL o `firstNotNullOf`/`firstOrNull`
en Kotlin. Por defecto toma el primer elemento que no sea `None` y cuyo valor
lógico sea verdadero, pero puedes personalizar la condición pasando un
`predicado` propio.

```cobra
import standard_library.logica as logica

var nombre = logica.coalesce(None, "", "Ada")          # -> "Ada"
var override = logica.coalesce("", predicado=lambda v: v is not None)
var primera_par = logica.coalesce(
    3,
    5,
    6,
    predicado=lambda numero: numero % 2 == 0,
)  # -> 6
```

Si todos los valores incumplen el predicado, `coalesce` devuelve `None`. En
cambio, si no se proporcionan argumentos, se emite un `ValueError` explícito
para facilitar la depuración.
