# Inventario de activos legacy por carpeta (internal-only)

Este inventario clasifica activos legacy para orientar la migración en dos etapas:

1. **Retirar primero exposición documental y referencias públicas**.
2. **Luego limpiar código muerto** únicamente con flag de migración interna activa.

Estado permitido por activo:

- `mantener interno`: se conserva fuera de contrato público mientras exista dependencia interna explícita.
- `deprecado`: congelado; no se amplía y se prepara retiro.
- `retirar`: remover al vencer la ventana de compatibilidad y tras validar cero dependencias.

## 1) Transpiladores legacy (`src/pcobra/cobra/transpilers/transpiler/`)

| Activo | Carpeta | Estado | Nota |
|---|---|---|---|
| `to_go.py` | `src/pcobra/cobra/transpilers/transpiler/` | deprecado | Mantener solo por compatibilidad interna temporal. |
| `to_cpp.py` | `src/pcobra/cobra/transpilers/transpiler/` | deprecado | Sin exposición en UX pública; retiro por calendario legacy. |
| `to_java.py` | `src/pcobra/cobra/transpilers/transpiler/` | deprecado | No backend oficial de salida; congelado para migración interna. |
| `to_wasm.py` | `src/pcobra/cobra/transpilers/transpiler/` | deprecado | Sin roadmap de promoción pública; mantener aislado. |
| `to_asm.py` | `src/pcobra/cobra/transpilers/transpiler/` | retirar | Prioridad de retiro temprana al vencer su ventana (`Q3 2026`). |

## 2) Docker de backends no oficiales (`docker/backends/`)

| Activo | Carpeta | Estado | Nota |
|---|---|---|---|
| `cpp.Dockerfile` | `docker/backends/` | deprecado | Imagen de soporte interno; no documentar como opción pública. |

> `python.Dockerfile`, `javascript.Dockerfile` y `rust.Dockerfile` no son legacy y quedan fuera de este inventario.

## 3) Ejemplos legacy (`examples/`)

| Activo | Carpeta | Estado | Nota |
|---|---|---|---|
| `examples/hello_world/go/` y `go.*` | `examples/hello_world/` | deprecado | Mantener solo en ruta interna/histórica durante migración. |
| `examples/hello_world/cpp/` y `cpp.*` | `examples/hello_world/` | deprecado | No mostrar en guías públicas de “primeros pasos”. |
| `examples/hello_world/java/` y `java.*` | `examples/hello_world/` | mantener interno | Útiles para validación de entrada histórica reverse y regresión interna. |
| `examples/hello_world/wasm/` y `wasm.*` | `examples/hello_world/` | deprecado | Sin soporte público activo; mantener solo pruebas de compatibilidad. |
| `examples/hello_world/asm/` y `asm.*` | `examples/hello_world/` | retirar | Reducir primero exposición pública y retirar tras ventana contractual. |

## 4) Reverse transpile desde Java (aclaración normativa)

`java` se mantiene **solo** como **entrada histórica** de `transpilar-inverso` cuando exista requisito interno explícito.

- No es backend oficial de salida.
- No debe aparecer en tablas/listas públicas de targets oficiales.
- Debe permanecer documentado como: **“entrada histórica, no salida oficial”**.

## 5) Regla operativa de limpieza (flag de migración)

Toda limpieza física de código legacy debe ejecutarse únicamente con el flujo de migración interna habilitado por:

- `COBRA_INTERNAL_LEGACY_TARGETS=1`
- y/o `--legacy-targets` en sesiones internas donde aplique.

Sin ese flag, la prioridad es **ocultar exposición pública** y preservar compatibilidad temporal interna.
