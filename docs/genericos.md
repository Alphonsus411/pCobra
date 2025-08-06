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

Al transpilar a Python, Rust o C++ los parámetros se convierten en las
construcciones genéricas propias de cada lenguaje. En lenguajes sin soporte
de genéricos, como JavaScript, los parámetros de tipo se omiten y se utilizan
tipos dinámicos.

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

```cpp
template <typename T>
void identidad(T x) {}

template <typename T>
class Caja {};
```

```javascript
// Los parámetros genéricos se ignoran por la naturaleza dinámica de JS
function identidad(x) {
    return x;
}
```
