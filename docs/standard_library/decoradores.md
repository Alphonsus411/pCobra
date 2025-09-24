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

## `orden_total`

Permite definir comparaciones completas en clases de datos usando
:func:`functools.total_ordering`. Acepta tanto ``@orden_total`` como
``@orden_total()`` y valida que se aplique sobre una clase.

```python
from pcobra.standard_library.decoradores import dataclase, orden_total

@orden_total
@dataclase
class Punto:
    x: int
    y: int

    def __lt__(self, otro: "Punto") -> bool:
        return (self.x, self.y) < (otro.x, otro.y)

    def __eq__(self, otro: object) -> bool:
        if not isinstance(otro, Punto):
            return NotImplemented
        return (self.x, self.y) == (otro.x, otro.y)

assert Punto(0, 1) <= Punto(0, 1) < Punto(1, 0)
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

## `depreciado`

Emite una advertencia de `DeprecationWarning` cada vez que se ejecuta la
función decorada. Es útil para guiar a quienes consumen el código hacia nuevas
alternativas sin romper la compatibilidad inmediata.

Cuando [Rich](https://rich.readthedocs.io/) está disponible se aprovecha para
enviar un aviso con formato en la consola. También puedes pasar tu propia
instancia de `Console` mediante el parámetro `consola`.

```python
from pcobra.standard_library.decoradores import depreciado

@depreciado(mensaje="Usa `procesar_datos_v2`")
def procesar_datos():
    ...
```

## `sincronizar`

Garantiza que una función se ejecute con exclusión mutua utilizando
`threading.Lock`. Resulta práctico para proteger secciones críticas cuando el
estado compartido se manipula desde múltiples hilos.

Puedes suministrar un candado propio (por ejemplo, un `threading.RLock`) con el
parámetro `candado` para coordinar varias funciones que deban compartir el mismo
lock.

```python
from threading import Lock
from pcobra.standard_library.decoradores import sincronizar

candado = Lock()

@sincronizar(candado=candado)
def actualizar_cache():
    ...
```

## `reintentar`

Reintenta la ejecución de una función sincrónica cuando se producen excepciones
controladas. Aplica un *backoff* exponencial configurable, con soporte de
`jitter` para repartir la carga en sistemas distribuidos.

Parámetros principales:

- **`intentos`** (`int`): número máximo de intentos. Debe ser mayor o igual a 1.
- **`excepciones`** (`type[BaseException] | Sequence[type[BaseException]]`):
  tipos que activan un nuevo intento.
- **`retardo_inicial`** (`float`): espera antes del primer reintento.
- **`factor_backoff`** (`float`): factor multiplicador entre esperas.
- **`max_retardo`** (`float | None`): límite superior opcional a la espera.
- **`jitter`** (`Callable[[float], float] | tuple[float, float] | float | bool | None`):
  controla la aleatoriedad aplicada a la espera.
- **`consola`** (`rich.console.Console | None`): instancia opcional para emitir
  mensajes estilizados cuando Rich está instalado.

```python
from pcobra.standard_library.decoradores import reintentar

@reintentar(intentos=5, excepciones=(TimeoutError,), retardo_inicial=0.2)
def consultar_servicio():
    ...
```

> **Nota:** la compatibilidad con Rich es opcional. Si no está instalado, los
> mensajes se envían mediante `print`.

## `reintentar_async`

Versión asíncrona de `reintentar` que delega en
`pcobra.corelibs.reintentar_async`. Mantiene la misma firma y comportamiento
general, aplicando la lógica de reintentos sobre corrutinas.

```python
from pcobra.standard_library.decoradores import reintentar_async

@reintentar_async(intentos=4, excepciones=(OSError,))
async def descargar_archivo():
    ...
```

> **Dependencias opcionales:**
>
> - [Rich](https://rich.readthedocs.io/) para mensajes con estilo.
> - `pcobra.corelibs` ya provee `reintentar_async`, por lo que no es necesario
>   instalar nada adicional para los reintentos asíncronos más allá de Cobra.

## `despachar_por_tipo`

Equivalente en español de :func:`functools.singledispatch`. Construye una
función despachadora que selecciona la implementación adecuada según el tipo del
primer argumento posicional. Añade atajos en español:

- ``registrar``: versión localizada de ``register`` con validación de tipos.
- ``despachar``: equivalente localizado de ``dispatch``.
- ``registros``: acceso de solo lectura al mapeo de implementaciones.

```python
from pcobra.standard_library.decoradores import despachar_por_tipo

@despachar_por_tipo()
def describir(valor):
    return f"Valor genérico: {valor!r}"

@describir.registrar(int)
def _(valor: int) -> str:
    return f"Entero: {valor}"

assert describir(5) == "Entero: 5"
assert describir(5.0).startswith("Valor genérico")
```
