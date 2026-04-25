# Architecture Overview

## Contrato unificado (aplica a toda esta sección)

- Cobra es el **único lenguaje/interfaz pública**.
- Solo existen **3 backends internos oficiales**: `python`, `javascript`, `rust`.
- La decisión de backend es **interna** (no configurable por usuario final), salvo hints internos controlados.

Este resumen documenta **cómo funciona internamente** la CLI unificada sin ampliar la superficie pública (`cobra run`, `cobra build`, `cobra test`, `cobra mod`).

## Flujo oficial inmutable

La ruta oficial y estable de arquitectura es:

```text
Frontend Cobra -> BackendPipeline -> Bindings
```

## Diagrama corto

```text
Frontend Cobra
      ↓
BackendPipeline
      ↓
Bindings (python/js/rust)
```

## Tabla de decisión de backend interno

> Esta tabla es de contrato interno. No expone configuración al usuario final.

| Señal técnica evaluada por el pipeline | Backend interno resultante | Ajuste permitido |
|---|---|---|
| Flujo estándar con prioridad de paridad de librerías | `python` | Hints internos controlados |
| Integración orientada a bridge/runtime web | `javascript` | Hints internos controlados |
| Requisito nativo/FFI con ABI contractual | `rust` | Hints internos controlados |

## 1) Frontend Cobra

El frontend procesa el código fuente, valida sintaxis y construye el AST base que se entrega al pipeline interno.

## 2) BackendPipeline

En la ruta pública, `cobra build` delega la elección del backend a `backend_pipeline.resolve_backend_runtime(...)` y/o `backend_pipeline.build(...)`, evitando exponer flags de backend como paso principal para usuario final.

`pcobra.cobra.build.backend_pipeline` se considera contrato interno inmutable para compile/transpile/runtime.

## 2.1) Contrato de datos compartidos para CLI de comandos

Para evitar divergencias entre comandos (`commands/` y `commands_v2/`), se define un
contrato explícito de **únicos puntos autorizados** para catálogo de transpiladores:

- `pcobra.cobra.transpilers.registry` → fuente canónica de inventario interno.
- `pcobra.cobra.cli.transpiler_registry` → fachada obligatoria para consumo desde CLI.

Reglas operativas:

1. Los comandos CLI no deben declarar constantes locales tipo `TRANSPILERS`, `BACKENDS`,
   `LANG_CHOICES` o `LANGUAGES`.
2. Los comandos CLI no deben importar otros módulos `*_cmd.py` (solo se permite
   compartir base común vía `commands.base`).
3. Si un comando necesita targets/transpiladores, debe usar exclusivamente
   `cli_transpilers()` y/o `cli_transpiler_targets()`.

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
- `docs/architecture/backend-pipeline-checklist.md`
- `docs/architecture/single_source_of_truth.md`
