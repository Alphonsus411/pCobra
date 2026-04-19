# Política normativa de exposición: público vs interno

> ⚠️ Documento parcialmente derivado: los bloques marcados como `BEGIN/END GENERATED`
> son **obligatorios**, se regeneran automáticamente y no deben editarse manualmente.

Este es el **documento normativo único** para distinguir módulos y superficies **públicas** frente a **internas** en el ecosistema unificado de Cobra.

## Fuente normativa de backends

La clasificación canónica de backends está definida en:

- `src/pcobra/cobra/architecture/backend_policy.py`

En particular:

- `PUBLIC_BACKENDS`: backends públicos soportados.
- `INTERNAL_BACKENDS`: backends internos/legacy, fuera de contrato público.

## Clasificación normativa

### Público (estable)

- CLI pública: `cobra` con comandos `run`, `build`, `test`, `mod`.
- Backends públicos: `python`, `javascript`, `rust`.
- Módulos stdlib públicos: `cobra.core`, `cobra.datos`, `cobra.web`, `cobra.system`.

### Interno (no contractual)

- Implementación de compilación/transpilación: lexer, parser, AST, IR, adapters y transpiladores internos.
- Backends internos/legacy definidos en `INTERNAL_BACKENDS`.

## Tiers oficiales de backends públicos

<!-- BEGIN GENERATED TARGET TIERS -->
### Tier 1

- `python`
- `javascript`
- `rust`

### Tier 2
<!-- END GENERATED TARGET TIERS -->

## API pública estable

| Categoría | Superficie estable |
|---|---|
| Comandos CLI | `run`, `build`, `test`, `mod` |
| Backends | `python`, `javascript`, `rust` |
| Módulos stdlib | `cobra.core`, `cobra.datos`, `cobra.web`, `cobra.system` |

## Estado público por backend

<!-- BEGIN GENERATED TARGET STATUS TABLE -->
| Backend | Tier | Runtime público | Estado Holobit público | Compatibilidad SDK real |
|---|---|---|---|---|
| `python` | Tier 1 | oficial verificable | `full`; usa el contrato completo del SDK Python | completa |
| `javascript` | Tier 1 | oficial verificable | adaptador mantenido por el proyecto; estado contractual `partial` | parcial |
| `rust` | Tier 1 | oficial verificable | adaptador mantenido por el proyecto; estado contractual `partial` | parcial |
<!-- END GENERATED TARGET STATUS TABLE -->

## Alcance contractual de runtime

<!-- BEGIN GENERATED TARGET RUNTIME SPLIT -->
- `OFFICIAL_RUNTIME_TARGETS`: `python`, `javascript`, `rust`
- `VERIFICATION_EXECUTABLE_TARGETS`: `python`, `javascript`, `rust`
- `BEST_EFFORT_RUNTIME_TARGETS`: 
- `TRANSPILATION_ONLY_TARGETS`: 
- `NO_RUNTIME_TARGETS`: 
- `OFFICIAL_STANDARD_LIBRARY_TARGETS`: `python`, `javascript`, `rust`
- `ADVANCED_HOLOBIT_RUNTIME_TARGETS`: `python`, `javascript`, `rust`
- `SDK_COMPATIBLE_TARGETS`: `python`
<!-- END GENERATED TARGET RUNTIME SPLIT -->

## Declaración explícita de estabilidad en esta fase

Se declara de forma explícita que **lexer, parser, AST y transpiladores internos no cambian de contrato externo** durante esta fase.

Esto significa que cualquier modificación en dichos componentes debe preservar la API pública estable definida en esta política.

## Regla de gobernanza

Cualquier cambio que amplíe o reduzca la API pública estable (comandos, backends públicos o módulos stdlib públicos) requiere:

1. actualización de esta política,
2. actualización de ADR de arquitectura aplicable,
3. comunicación explícita en notas de versión.
