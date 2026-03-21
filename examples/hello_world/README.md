# Ejemplos de Hola mundo

Esta carpeta usa exclusivamente los 8 targets oficiales con sus nombres
canónicos: `python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java` y `asm`.

Lectura recomendada de la política asociada:

- **Transpilación oficial**: los 8 targets anteriores.
- **Runtime oficial**: `python`, `rust`, `javascript`, `cpp`.
- **Runtime experimental/best-effort**: `go`, `java`.
- **Solo transpilación sin runtime público**: `wasm`, `asm`.

Cada ejemplo se puede generar ejecutando:

```bash
cobra examples/hello_world/<lenguaje>.co --to <lenguaje>
```

Resultados pre-generados para cada transpilador oficial:

- `python`: `cobra examples/hello_world/python.co --to python` → [python.py](python.py)
- `rust`: `cobra examples/hello_world/rust.co --to rust` → [rust.rs](rust.rs)
- `javascript`: `cobra examples/hello_world/javascript.co --to javascript` → [javascript.js](javascript.js)
- `wasm`: `cobra examples/hello_world/wasm.co --to wasm` → [wasm.wat](wasm.wat)
- `go`: `cobra examples/hello_world/go.co --to go` → [go.go](go.go)
- `cpp`: `cobra examples/hello_world/cpp.co --to cpp` → [cpp.cpp](cpp.cpp)
- `java`: `cobra examples/hello_world/java.co --to java` → [java.java](java.java)
- `asm`: `cobra examples/hello_world/asm.co --to asm` → [asm.asm](asm.asm)
