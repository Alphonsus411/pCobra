# Utilidades de la biblioteca estándar: `rel`

## Propósito
`rel` es un administrador de contexto que permite aplicar cambios temporales sobre un objeto o función dentro de un bloque `with`. Al finalizar el bloque (o al agotarse un temporizador opcional) los cambios se revierten automáticamente, lo que facilita parchear objetos durante pruebas o adaptar comportamientos puntuales sin modificar el estado permanente.

## Parámetros
- **`objetivo`** (`Any`): instancia o función cuyos atributos serán modificados de forma temporal.
- **`cambios`** (`Mapping[str, Any]` | `Callable[[Any], Optional[Callable[[], None]]]`):
  - Si es un mapeo, cada par `nombre: valor` se aplica como asignación sobre el `objetivo`, conservando el valor original para restaurarlo al salir del contexto.
  - Si es un callable, recibe el `objetivo`, ejecuta los cambios necesarios y puede devolver otra función encargada de deshacerlos.
- **`condicion`** (`Callable[[Any], bool]`, opcional): función que decide si los cambios deben aplicarse. Cuando es `None` se asume `True` y los cambios siempre se ejecutan.
- **`duracion`** (`float`, opcional): tiempo en segundos tras el cual se revierte el parche automáticamente, incluso si el bloque `with` sigue en ejecución.

## Valor de retorno
- Devuelve el propio `objetivo` dentro del contexto para permitir trabajar con él directamente. No se produce un valor distinto al cerrar el bloque.

## Ejemplos
### Sustituir un atributo durante una prueba
```python
from pcobra.standard_library.util import rel

class Demo:
    valor = 1

demo = Demo()
with rel(demo, {"valor": 99}):
    assert demo.valor == 99
# Fuera del contexto, el valor original se restaura
assert demo.valor == 1
```

### Parchear una función con lógica personalizada
```python
from pcobra.standard_library.util import rel

def hola():
    """Saluda."""
    return "hola"

def parchear_doc(funcion):
    original = funcion.__doc__
    funcion.__doc__ = "documentación temporal"
    # La función devuelta se usa para revertir el cambio
    return lambda: setattr(funcion, "__doc__", original)

with rel(hola, parchear_doc):
    assert hola.__doc__ == "documentación temporal"
assert hola.__doc__ == "Saluda."
```

### Revertir automáticamente tras un intervalo
```python
from pcobra.standard_library.util import rel
import time

class Demo:
    valor = 1

demo = Demo()
with rel(demo, {"valor": 5}, duracion=0.01):
    time.sleep(0.02)
    # La restauración ocurre al vencer el temporizador
    assert demo.valor == 1
```

## Notas
- Si el callable proporcionado en `cambios` devuelve un valor que no es `None` ni un callable, se lanza `TypeError` y los cambios se revierten.
- Cuando el atributo original no existía, `rel` lo elimina durante la restauración.
- El temporizador creado por `duracion` es un hilo en segundo plano; se cancela automáticamente al salir del bloque para evitar ejecuciones tardías.
