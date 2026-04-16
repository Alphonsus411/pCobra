# ADR: Cobra unifica la superficie pública en 3 backends

- **Estado:** Aprobado
- **Fecha:** 2026-04-16
- **Decisores:** Equipo Core de pCobra
- **Relacionado con:** `docs/architecture/adr-unified-backends.md`, `docs/targets_policy.md`

## Decisión

1. **Cobra es la única interfaz pública** para usuarios e integraciones externas.
2. Los **backends oficiales públicos** son exclusivamente: `python`, `javascript`, `rust`.
3. Los transpiladores legacy (`go`, `cpp`, `java`, `wasm`, `asm`) se mantienen como **internos** y **no soportados públicamente**.

## Compatibilidad interna (no pública)

Los backends legacy se aceptan solo para migración operativa interna con ventana de retiro:

- `go`: retiro objetivo **Q4 2026**
- `cpp`: retiro objetivo **Q4 2026**
- `java`: retiro objetivo **Q1 2027**
- `wasm`: retiro objetivo **Q2 2027**
- `asm`: retiro objetivo **Q3 2026**

Fuera de ese contexto, no deben aparecer en rutas ni documentación públicas.

## Criterio de salida

Cualquier API pública, CLI pública o documentación orientada a usuario **solo puede listar 3 targets** y deben ser exactamente:

`python`, `javascript`, `rust`.
