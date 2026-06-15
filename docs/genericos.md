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

Al transpilar a los targets oficiales públicos `python`, `javascript` y `rust`, los parámetros se convierten en las
construcciones genéricas propias de cada lenguaje cuando existen. En `javascript`, los parámetros de tipo se omiten y se utilizan
tipos dinámicos. Las variantes históricas para `cpp` quedan fuera de la documentación pública.

```python
from typing import TypeVar, Generic
T = TypeVar('T')

def identidad(x: T) -> T:
    return x

class Caja(Generic[T]):
    pass
```

```rust
fn identidad<T>(x: T) {
}

struct Caja<T> {}
impl<T> Caja<T> {}
```

```javascript
// Los parámetros genéricos se ignoran por la naturaleza dinámica de `javascript`
function identidad(x) {
    return x;
}
```
