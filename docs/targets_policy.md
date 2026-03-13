# Política oficial de targets

Este documento define la política de lenguajes soportados que debe mantenerse
coherente entre código, CLI y documentación principal.

## Salida directa (8)

Lista oficial de destinos para `cobra compilar`:

1. `python`
2. `rust`
3. `javascript`
4. `wasm`
5. `go`
6. `cpp`
7. `java`
8. `asm`

Fuente de verdad en código: `src/pcobra/cobra/transpilers/targets.py`.

## Reverse de entrada (3)

Lista oficial de orígenes para `cobra transpilar-inverso`:

1. `python`
2. `js` (alias histórico de JavaScript)
3. `java`

Fuente de verdad en código: `src/pcobra/cobra/transpilers/reverse/policy.py`.

## Regla de mantenimiento

- No se deben documentar otros lenguajes como targets oficiales de salida o de
  reverse en la documentación principal.
- Los scripts de benchmark (`scripts/benchmarks/run_benchmarks.py`,
  `scripts/benchmarks/compare_backends.py`,
  `scripts/benchmarks/binary_bench.py`) deben derivar siempre la lista de
  backends desde `src/pcobra/cobra/transpilers/targets.py`
  (`OFFICIAL_TARGETS`, `TIER1_TARGETS`, `TIER2_TARGETS`) y limitarse a mantener
  metadatos técnicos (extensiones/comandos) locales.
- Cualquier ampliación o reducción del alcance debe actualizar:
  - este archivo,
  - la fuente de verdad en código,
  - y la validación automática en CI.
