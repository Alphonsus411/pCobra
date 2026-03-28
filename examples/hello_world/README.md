# Ejemplos de Hola mundo

Esta carpeta usa exclusivamente los 8 targets oficiales con sus nombres
canónicos: `python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java` y `asm`.

Lectura recomendada de la política asociada:

- **Transpilación oficial**: los 8 targets anteriores.
- **Runtime oficial**: `python`, `rust`, `javascript`, `cpp`.
- **Runtime experimental/best-effort**: `go`, `java`.
- **Solo transpilación sin runtime público**: `wasm`, `asm`.
- **Orígenes reverse de entrada**: se documentan por separado (`python`, `javascript`, `java`) y no alteran esta tabla de salidas oficiales.

Cada ejemplo se puede generar ejecutando (reemplaza ``<target_oficial>`` por uno
de los 8 nombres canónicos):

```bash
cobra compilar examples/hello_world/<target_oficial>.co --tipo <target_oficial>
```

Resultados pre-generados para cada transpilador oficial:

- `python`: `cobra compilar examples/hello_world/python.co --tipo python` → [python.py](python.py)
- `rust`: `cobra compilar examples/hello_world/rust.co --tipo rust` → [rust.rs](rust.rs)
- `javascript`: `cobra compilar examples/hello_world/javascript.co --tipo javascript` → [javascript.js](javascript.js)
- `wasm`: `cobra compilar examples/hello_world/wasm.co --tipo wasm` → [wasm.wat](wasm.wat)
- `go`: `cobra compilar examples/hello_world/go.co --tipo go` → [go.go](go.go)
- `cpp`: `cobra compilar examples/hello_world/cpp.co --tipo cpp` → [cpp.cpp](cpp.cpp)
- `java`: `cobra compilar examples/hello_world/java.co --tipo java` → [java.java](java.java)
- `asm`: `cobra compilar examples/hello_world/asm.co --tipo asm` → [asm.asm](asm.asm)
