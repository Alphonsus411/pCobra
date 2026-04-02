# Language Equivalence Matrix (contract v1.0.0)

Este documento es el **contrato versionado** de equivalencia Cobra ↔ Python ↔ backends.
La fuente estructurada se mantiene en `data/language_equivalence.yml` y se valida automáticamente contra
`src/pcobra/cobra/transpilers/compatibility_matrix.py`.

## Alcance

Cada feature documenta:
- Sintaxis Cobra.
- Equivalente Python.
- Equivalentes por backend: `javascript`, `rust`, `go`, `cpp`, `java`, `wasm`, `asm`.
- Estado por backend (`full`, `partial`, `none`) y limitaciones.

## Features cubiertas

1. `decoradores`
2. `imports_corelibs`
3. `manejo_errores`
4. `async`
5. `tipos_compuestos`
6. `hooks_runtime`

## Resumen de estado por feature/backend

| Feature | python | javascript | rust | go | cpp | java | wasm | asm |
|---|---|---|---|---|---|---|---|---|
| decoradores | full | full | partial | partial | partial | none | partial | partial |
| imports_corelibs | full | partial | partial | partial | partial | partial | partial | partial |
| manejo_errores | full | partial | partial | partial | partial | partial | partial | partial |
| async | full | full | none | partial | none | none | none | partial |
| tipos_compuestos | full | full | partial | partial | partial | partial | partial | partial |
| hooks_runtime | full | full | full | full | full | full | full | full |

## Sincronización y backlog técnico

- Validación de contrato:
  - `python scripts/ci/validate_language_equivalence_matrix.py`
- Generación automática de backlog por gaps (`status != full`):
  - `python scripts/ci/generate_language_equivalence_backlog.py`

El backlog generado se guarda en `data/language_equivalence_backlog.md` y se puede ejecutar en CI para mantener tareas al día.
