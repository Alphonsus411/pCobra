# Política oficial de targets

Este documento define la política de lenguajes soportados que debe mantenerse
coherente entre código, CLI, CI y documentación pública.

## Fuente de verdad

La fuente única de verdad para los targets oficiales de salida es
`src/pcobra/cobra/transpilers/targets.py`. En ese módulo se definen
explícitamente `TIER1_TARGETS`, `TIER2_TARGETS`, `OFFICIAL_TARGETS` y los
aliases legacy reservados solo para compatibilidad interna controlada.

## Salida directa oficial

Los únicos destinos oficiales de `cobra compilar` son:

### Tier 1

1. `python`
2. `rust`
3. `javascript`
4. `wasm`

### Tier 2

1. `go`
2. `cpp`
3. `java`
4. `asm`

## Política de nombres canónicos

En documentación pública, ejemplos de CLI, tablas, archivos de configuración y
texto narrativo deben usarse exclusivamente los nombres canónicos:

- `python`
- `rust`
- `javascript`
- `wasm`
- `go`
- `cpp`
- `java`
- `asm`

No se deben publicar aliases legacy ni targets retirados en snippets o tablas de
usuario final.

## Reverse de entrada

La transpilación inversa se documenta como capacidad independiente. Su política
de entrada se define en `src/pcobra/cobra/transpilers/reverse/policy.py`.
La documentación pública debe referirse a los orígenes reverse mediante sus
nombres canónicos actuales:

- `python`
- `javascript`
- `java`

## Regla de mantenimiento

- No se deben documentar otros lenguajes como targets oficiales de salida.
- Los scripts de benchmark (`scripts/benchmarks/run_benchmarks.py`,
  `scripts/benchmarks/compare_backends.py`,
  `scripts/benchmarks/binary_bench.py`) deben derivar siempre la lista de
  backends desde `src/pcobra/cobra/transpilers/targets.py`
  (`OFFICIAL_TARGETS`, `TIER1_TARGETS`, `TIER2_TARGETS`) y limitarse a mantener
  metadatos técnicos locales.
- La CI debe incluir comprobaciones textuales para impedir la reaparición de
  aliases legacy, módulos reverse borrados, extras no vigentes o ejemplos de
  CLI fuera de política en rutas de documentación pública y ejemplos.
- Cualquier ampliación o reducción del alcance debe actualizar:
  - este archivo,
  - la fuente de verdad en código,
  - y la validación automática en CI.
