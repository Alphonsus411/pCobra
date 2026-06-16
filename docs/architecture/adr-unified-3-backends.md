# ADR: Cobra unifica la superficie pública en 3 backends

## Contrato unificado (aplica a toda esta ADR)

- Cobra es el **único lenguaje/interfaz pública**.
- Solo existen **3 backends internos oficiales**: `python`, `javascript`, `rust`.
- La decisión de backend es **interna** (no configurable por usuario final), salvo hints internos controlados.

- **Estado:** Aprobado
- **Fecha:** 2026-04-16
- **Decisores:** Equipo Core de pCobra
- **Relacionado con:** `docs/architecture/adr-unified-backends.md`, `docs/targets_policy.md`

## Decisión

1. **Cobra es la única interfaz pública** para usuarios e integraciones externas.
2. Los **backends oficiales públicos** son exclusivamente: `python`, `javascript`, `rust`.
3. Los transpiladores legacy (`go`, `cpp`, `java`, `wasm`, `asm`) se retiran de la ruta de BackEnd: no son configurables, no aparecen en comandos públicos y cualquier referencia restante debe vivir solo en documentación histórica/no-backend.

## Zona histórica (no BackEnd)

Las referencias heredadas a `go`, `cpp`, `java`, `wasm` y `asm` se tratan como inventario histórico o material de migración cerrado. No deben importarse desde `src/pcobra/cobra/transpilers/transpiler/legacy/` ni anunciarse como BackEnd.

## Criterio de salida

Cualquier API pública, CLI pública o documentación orientada a usuario **solo puede listar 3 targets** y deben ser exactamente:

`python`, `javascript`, `rust`.
