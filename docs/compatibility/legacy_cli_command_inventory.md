# Inventario de comandos legacy (`src/pcobra/cobra/cli/commands/`)

Este inventario clasifica la superficie v1 de la CLI en tres categorías para la etapa de recorte de UX pública.

## Público (permitidos en perfil `public`)

- `interactive`
- `compilar`
- `ejecutar`
- `modulos`
- `verificar`
- `docs`
- `plugins`
- `init`
- `crear`
- `paquete`

## Interno (solo perfil `development`)

- `cache`
- `contenedor`
- `gui`
- `jupyter`
- `qualia`
- `agix`

## Obsoleto (solo migración interna/regresión)

- `dependencias`
- `empaquetar`
- `bench`
- `benchmarks`
- `benchmarks2`
- `benchtranspilers`
- `benchthreads`
- `profile`
- `transpilar-inverso`
- `validar-sintaxis`
- `qa-validar`

## Política aplicada

- En CLI v1 con perfil `public`, se desactivan comandos internos y obsoletos.
- En CLI v1 con perfil `development`, se conservan para migración técnica y pruebas de regresión.
- En CLI v2, la UX pública ya permanece limitada a `run`, `build`, `test`, `mod`.
