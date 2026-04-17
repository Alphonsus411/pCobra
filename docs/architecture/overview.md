# Architecture Overview

Este resumen documenta **cómo funciona internamente** la CLI unificada sin ampliar la superficie pública (`cobra run`, `cobra build`, `cobra test`, `cobra mod`).

## Diagrama corto

```text
Frontend Cobra
      ↓
BackendPipeline
      ↓
Bindings (python/js/rust)
```

## 1) Frontend Cobra

El frontend procesa el código fuente, valida sintaxis y construye el AST base que se entrega al pipeline interno.

## 2) BackendPipeline

En la ruta pública, `cobra build` delega la elección del backend a `backend_pipeline.resolve_backend(...)`, evitando exponer flags de backend como paso principal para usuario final.

## 3) Bindings (python/js/rust)

Tras resolver backend, el pipeline valida capacidades/runtime y produce contexto de bridge (`route`, `bridge`, `abi_contract`, `abi_version`). Así la unión con runtime nativo queda encapsulada por contrato de ruta.

## Imports y stdlib (resolución determinista)

La resolución de imports usa prioridad determinista (`stdlib > project > python_bridge > hybrid`) y evita ambigüedad silenciosa. En documentación pública se priorizan módulos canónicos:

- `cobra.core`
- `cobra.datos`
- `cobra.web`
- `cobra.system`

## Referencias técnicas

- `src/pcobra/cobra/cli/commands_v2/build_cmd.py`
- `src/pcobra/cobra/build/backend_pipeline.py`
- `src/pcobra/cobra/imports/resolver.py`
- `src/pcobra/cobra/transpilers/module_map.py`
