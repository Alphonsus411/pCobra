# Política normativa de exposición: público vs interno

Este es el **documento normativo único** para distinguir módulos y superficies **públicas** frente a **internas** en el ecosistema unificado de Cobra.

## Fuente normativa de backends

La clasificación canónica de backends está definida en:

- `src/pcobra/cobra/architecture/backend_policy.py`

En particular:

- `PUBLIC_BACKENDS`: backends públicos soportados.


## Clasificación normativa

### Público (estable)

- CLI pública: `cobra` con comandos `run`, `build`, `test`, `mod`.
- Backends públicos: `python`, `javascript`, `rust`.
- Módulos stdlib públicos: `cobra.core`, `cobra.datos`, `cobra.web`, `cobra.system`.


## Tiers oficiales de soporte

<!-- BEGIN GENERATED TARGET TIERS -->
### Tier 1

- `python`
- `javascript`
- `rust`

### Tier 2
<!-- END GENERATED TARGET TIERS -->

## Matriz pública de backends

<!-- BEGIN GENERATED TARGET STATUS TABLE -->
| Backend | Tier | Runtime público | Estado Holobit público | Compatibilidad SDK real |
|---|---|---|---|---|
| `python` | Tier 1 | oficial verificable | `full`; usa el contrato completo del SDK Python | completa |
| `javascript` | Tier 1 | oficial verificable | adaptador mantenido por el proyecto; estado contractual `partial` | parcial |
| `rust` | Tier 1 | oficial verificable | adaptador mantenido por el proyecto; estado contractual `partial` | parcial |
<!-- END GENERATED TARGET STATUS TABLE -->

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

## API pública estable

| Categoría | Superficie estable |
|---|---|
| Comandos CLI | `run`, `build`, `test`, `mod` |
| Backends | `python`, `javascript`, `rust` |
| Módulos stdlib | `cobra.core`, `cobra.datos`, `cobra.web`, `cobra.system` |

## Declaración explícita de estabilidad en esta fase

Se declara de forma explícita que **lexer, parser, AST y transpiladores internos no cambian de contrato externo** durante esta fase.

Esto significa que cualquier modificación en dichos componentes debe preservar la API pública estable definida en esta política.

## Regla de gobernanza

Cualquier cambio que amplíe o reduzca la API pública estable (comandos, backends públicos o módulos stdlib públicos) requiere:

1. actualización de esta política,
2. actualización de ADR de arquitectura aplicable,
3. comunicación explícita en notas de versión.

## Contrato de arranque (startup)

- En rutas de arranque públicas (importación de pcobra y comandos públicos de arranque como repl/run/test) **solo** se pueden inicializar por defecto los backends `python`, `javascript`, `rust`.


Los orígenes reverse pertenecen a una ruta de entrada separada y no amplían los targets de salida oficiales. Este recorrido normativo principal mantiene la lista pública en `python`, `javascript` y `rust`.
