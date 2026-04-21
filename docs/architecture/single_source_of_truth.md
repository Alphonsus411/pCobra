# Política de arquitectura: single source of truth (`pcobra.cobra`)

## Objetivo

Desde este cambio, **`src/pcobra/cobra/**` es la única implementación productiva** de Cobra.
El árbol `src/cobra/**` queda reservado exclusivamente para compatibilidad hacia atrás
(shims/reexports).

## Inventario actual de duplicados

Se inventarió cada módulo Python presente en `src/cobra/**` y su espejo en
`src/pcobra/cobra/**`.

| Módulo legacy (`src/cobra`) | Módulo canónico (`src/pcobra/cobra`) | Estado |
| --- | --- | --- |
| `transpilers/registry.py` | `transpilers/registry.py` | Shim por reexport (sin lógica productiva) |
| `transpilers/targets.py` | `transpilers/targets.py` | Shim por reexport (sin lógica productiva) |
| `transpilers/compatibility_matrix.py` | `transpilers/compatibility_matrix.py` | Shim por reexport (sin lógica productiva) |
| `transpilers/__init__.py` | `transpilers/__init__.py` | Shim por reexport |
| `cli/target_policies.py` | `cli/target_policies.py` | Shim por reexport |
| `cli/__init__.py` | `cli/__init__.py` | Shim mínimo por reexport |
| `cli/cli.py` | `cli/cli.py` | Wrapper legacy de entrada (bootstrap de CLI) |
| `__init__.py` | `__init__.py` | Bootstrap de paquete legacy (alias compat) |

## Reglas de mantenimiento

1. Toda lógica nueva debe vivir en `src/pcobra/cobra/**`.
2. `src/cobra/**` no puede contener nuevas implementaciones funcionales.
3. Los módulos legacy deben limitarse a:
   - docstring,
   - import/reexport hacia `pcobra.cobra.*`,
   - y opcionalmente `__all__`.
4. Excepciones permitidas de bootstrap legacy:
   - `src/cobra/__init__.py`,
   - `src/cobra/cli/cli.py`.

## Empaquetado

El empaquetado oficial ya excluye `cobra*` y publica únicamente `pcobra*`.
Por tanto, los módulos de `src/cobra/**` se mantienen sólo para compatibilidad en
entornos de desarrollo/migración interna.

## Guardia CI

Se añade `scripts/ci/lint_legacy_cobra_shims.py`, que falla si:

- aparece un módulo en `src/cobra/**` sin espejo en `src/pcobra/cobra/**`,
- un módulo legacy (salvo bootstraps exentos) contiene código más allá de reexports,
- o un shim no reexporta explícitamente desde `pcobra.cobra.*`.

Esta guardia protege la política de **single source of truth** y evita divergencias
silenciosas entre ambos árboles.
