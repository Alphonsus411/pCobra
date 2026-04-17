# Contrato de rutas de binding (normativo)

Este documento resume el contrato normativo declarado en `bindings/contract.py`.
La **fuente normativa única** para rutas, matriz ABI y límites operativos es ese archivo.

## Rutas contractuales

- `python_direct_import`
- `javascript_runtime_bridge`
- `rust_compiled_ffi`

## Matriz ABI por ruta y compatibilidad hacia atrás

| Ruta | ABI actual | ABI soportadas | Compatibilidad hacia atrás |
| --- | --- | --- | --- |
| `python_direct_import` | `1.0` | `1.0` | `1.0` |
| `javascript_runtime_bridge` | `1.1` | `1.1`, `1.0` | `1.0` |
| `rust_compiled_ffi` | `2.0` | `2.0`, `1.1`, `1.0` | `1.1`, `1.0` |

Política:

1. Si no se especifica ABI, se negocia la ABI actual por ruta.
2. Si se especifica ABI y está en soportadas, se acepta si coincide con la actual
   o si está incluida en la lista de compatibilidad hacia atrás.
3. Cualquier ABI fuera de `soportadas` se rechaza.

## Límites operativos por ruta

### `python_direct_import`

- Proceso: mismo proceso del runtime principal.
- Aislamiento: no hay aislamiento de proceso; depende de `safe_mode` + validadores.
- FFI: no aplica.
- Sandbox: soportado (sandbox Python).
- Contenedor: no soportado como ruta directa.

### `javascript_runtime_bridge`

- Proceso: runtime JS gestionado (proceso/VM dedicado).
- Aislamiento: obligatorio (sandbox de runtime gestionado o contenedor).
- FFI: no usa FFI nativa; usa IPC/mensajería versionada.
- Sandbox: soportado.
- Contenedor: soportado (recomendado para reproducibilidad de pruebas).

### `rust_compiled_ffi`

- Proceso: proceso principal + librería nativa cargada.
- Aislamiento: frontera nativa por ABI/FFI.
- FFI: requiere ABI explícita y artefactos compilados.
- Sandbox: no soportado en sandbox Python.
- Contenedor: soportado para aislamiento operativo.
