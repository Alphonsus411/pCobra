# Política normativa de exposición: público vs interno

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
