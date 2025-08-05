# Tipos genéricos en Cobra

Cobra permite declarar funciones y clases que aceptan parámetros de tipo.
Los parámetros se delimitan con los símbolos `<` y `>` después del nombre.

```cobra
func identidad<T>(x):
    retorno x
fin

clase Caja<T>:
    fin
```

Al transpilar a Python y Rust los parámetros se conservan:

```python
from typing import TypeVar
T = TypeVar('T')

def identidad[T](x):
    return x
```

```rust
fn identidad<T>(x: T) {
}

struct Caja<T> {}
impl<T> Caja<T> {}
```
