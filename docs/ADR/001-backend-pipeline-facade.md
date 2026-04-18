# ADR 001: Fachada interna única para resolución/transpilación

## Contexto
El código tenía múltiples puntos internos que invocaban transpilers o adapters de backend de forma directa desde CLI/imports.
Eso fragmenta el contrato interno, duplica reglas de resolución y dificulta la gobernanza de backends.

## Decisión
Se define `pcobra.cobra.build.backend_pipeline` como única API interna aprobada para resolver/transpilar:

- `resolve_backend_runtime(source, hints)`
- `build(source, hints)`
- `transpile(ast, backend)`

Además, se establece explícitamente la regla:

> No usar transpilers directamente desde CLI/stdlib/imports.

Los módulos legacy (`pcobra.cobra.backends.resolver`) quedan como *shim* técnico mínimo y redirigen a la fachada del pipeline.

## Consecuencias
- CLI/imports usan una ruta única para resolución y transpilación.
- Se reduce el acoplamiento con clases de transpilers/adapters concretos.
- Cambios futuros de política/runtime se concentran en el pipeline.
