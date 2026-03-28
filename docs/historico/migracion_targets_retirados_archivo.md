# Archivo histórico: migración de targets retirados

> Estado: **histórico**. Este documento no define el flujo operativo activo.
> La política vigente se mantiene en `docs/targets_policy.md` y la guía activa en
> `docs/migracion_targets_retirados.md`.

## Cronología histórica de deprecación (cerrada)

- Inicio de deprecación documentado: `v10.0.10`.
- Eliminación definitiva documentada: `v10.2.0`.

## Ejemplos históricos de equivalencias usadas durante la transición

Durante la ventana de deprecación se comunicaron equivalencias como:

- `js -> javascript`
- `c++ -> cpp`
- `ensamblador -> asm`

Estas equivalencias se conservan **solo** para trazabilidad documental. En el
flujo activo deben usarse exclusivamente los 8 targets canónicos:
`python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java`, `asm`.
