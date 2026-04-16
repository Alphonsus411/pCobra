# Architecture Overview

Este resumen documenta **cómo funciona internamente** la CLI unificada sin ampliar la superficie pública (`cobra run`, `cobra build`, `cobra test`, `cobra mod`).

## 1) Selección automática de backend

En la ruta pública, `cobra build` delega la elección del backend a `backend_pipeline.resolve_backend(...)`, en lugar de pedir `--backend` como paso principal. El comando V2 traduce esa resolución hacia la ejecución interna manteniendo la UX estable.

## 2) Imports híbridos

La resolución de imports usa prioridad determinista (`stdlib > project > python_bridge > hybrid`) y adjunta metadatos de resolución/backend al módulo cargado. Esto permite convivir módulos del proyecto, puentes Python e imports híbridos sin ambigüedad silenciosa.

## 3) Bindings por ruta

Tras resolver backend, el pipeline valida capacidades/runtime y produce contexto de bridge (`route`, `bridge`, `abi_contract`, `abi_version`). De esta forma, la unión con runtime nativo queda encapsulada por contrato de ruta en vez de exponer lógica de backend al usuario final.

## Referencias técnicas

- `src/pcobra/cobra/cli/commands_v2/build_cmd.py`
- `src/pcobra/cobra/build/backend_pipeline.py`
- `src/pcobra/cobra/imports/resolver.py`
- `src/pcobra/cobra/transpilers/module_map.py`
