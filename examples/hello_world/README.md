# Ejemplos de Hola mundo

Para experiencia pública de usuario, esta carpeta recomienda solo:
`python`, `rust`, `javascript`.

Los artefactos `go`, `cpp`, `java`, `wasm` y `asm` permanecen como compatibilidad
**internal-only** (migración/regresión), no como recomendación de uso en CLI pública.

Comando público recomendado:

```bash
cobra build examples/hello_world/<target_publico>.co --backend <target_publico>
```

Resultados pre-generados:

- `python`: `cobra compilar examples/hello_world/python.co --backend python` → [python.py](python.py)
- `rust`: `cobra compilar examples/hello_world/rust.co --backend rust` → [rust.rs](rust.rs)
- `javascript`: `cobra compilar examples/hello_world/javascript.co --backend javascript` → [javascript.js](javascript.js)
- `wasm` *(internal-only)*: [wasm.wat](wasm.wat)
- `go` *(internal-only)*: [go.go](go.go)
- `cpp` *(internal-only)*: [cpp.cpp](cpp.cpp)
- `java` *(internal-only)*: [java.java](java.java)
- `asm` *(internal-only)*: [asm.asm](asm.asm)
