# Ejemplos de Hola mundo

Esta carpeta usa exclusivamente los 8 targets oficiales con sus nombres
canónicos: `python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java` y `asm`.

Lectura recomendada de la política asociada:

- **Transpilación oficial**: los 8 targets anteriores.
- **Runtime oficial**: `python`, `rust`, `javascript`, `cpp`.
- **Runtime best-effort**: `go`, `java`.
- **Solo transpilación sin runtime público**: `wasm`, `asm`.
- **Orígenes reverse de entrada**: se documentan por separado (`python`, `javascript`, `java`) y no alteran esta tabla de salidas oficiales.

Cada ejemplo se puede generar ejecutando (reemplaza ``<backend_oficial>`` por uno
de los 8 nombres canónicos):

```bash
cobra compilar examples/hello_world/<backend_oficial>.co --backend <backend_oficial>
```

Resultados pre-generados para cada transpilador oficial:

- `python`: `cobra compilar examples/hello_world/python.co --backend python` → [python.py](python.py)
- `rust`: `cobra compilar examples/hello_world/rust.co --backend rust` → [rust.rs](rust.rs)
- `javascript`: `cobra compilar examples/hello_world/javascript.co --backend javascript` → [javascript.js](javascript.js)
- `wasm`: `cobra compilar examples/hello_world/wasm.co --backend wasm` → [wasm.wat](wasm.wat)
- `go`: `cobra compilar examples/hello_world/go.co --backend go` → [go.go](go.go)
- `cpp`: `cobra compilar examples/hello_world/cpp.co --backend cpp` → [cpp.cpp](cpp.cpp)
- `java`: `cobra compilar examples/hello_world/java.co --backend java` → [java.java](java.java)
- `asm`: `cobra compilar examples/hello_world/asm.co --backend asm` → [asm.asm](asm.asm)
