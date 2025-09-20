# standard_library.decoradores

El módulo `standard_library.decoradores` ofrece atajos en español para patrones
comunes al definir funciones y clases en Python. Facilita alternar entre Cobra y
Python sin perder expresividad ni documentación.

## `memoizar`

Envoltorio de :func:`functools.lru_cache`. Permite memorizar el resultado de una
función según sus argumentos.

### Parámetros
- **`maxsize`** (`int | None`, opcional): cantidad máxima de entradas a
  conservar. Usa `None` para un caché ilimitado. Valor predeterminado: `128`.
- **`typed`** (`bool`, opcional): cuando es `True`, considera tipos distintos
  como claves diferentes (`1` y `1.0`).

### Uso básico
```python
from pcobra.standard_library.decoradores import memoizar

@memoizar(maxsize=None)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
```

## `dataclase`

Alias directo de :func:`dataclasses.dataclass` que mantiene todos los
argumentos originales.

```python
from pcobra.standard_library.decoradores import dataclase

@dataclase
class Punto:
    x: float
    y: float
```

## `temporizar`

Mide el tiempo de ejecución de una función usando `time.perf_counter` y reporta
el resultado con [Rich](https://rich.readthedocs.io/en/stable/) si está
instalado.

### Parámetros
- **`etiqueta`** (`str`, opcional): texto mostrado al reportar la duración. Por
  defecto usa `func.__qualname__`.
- **`precision`** (`int`, opcional): cantidad de decimales. Valor por defecto: 4.
- **`consola`** (`rich.console.Console`, opcional): instancia personalizada para
  imprimir. Si es `None`, se crea una temporal cuando Rich está disponible y en
  caso contrario se usa `print`.

### Ejemplo
```python
from pcobra.standard_library.decoradores import temporizar

@temporizar(etiqueta="render")
def renderizar():
    ...
```
