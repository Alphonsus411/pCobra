# ADR: Cobra unifica la superficie pública en 3 backends

## Contrato unificado (aplica a toda esta ADR)

- Cobra es el **único lenguaje/interfaz pública**.
- El **BackEnd oficial** de Cobra está compuesto exclusivamente por 3 targets: `python`, `javascript`, `rust`.
- La decisión de backend es **interna** (no configurable por usuario final), salvo hints internos controlados.

- **Estado:** Aprobado
- **Fecha:** 2026-04-16
- **Decisores:** Equipo Core de pCobra
- **Relacionado con:** `docs/architecture/adr-unified-backends.md`, `docs/targets_policy.md`

## Decisión

1. **Cobra es la única interfaz pública** para usuarios e integraciones externas.
2. El **BackEnd oficial** coincide con `docs/targets_policy.md` y está compuesto exclusivamente por: `python`, `javascript`, `rust`.
3. Los transpiladores legacy (`go`, `cpp`, `java`, `wasm`, `asm`) se retiran del BackEnd oficial: no son configurables, no aparecen en comandos públicos y se conservan solo como histórico si aplica.

## Zona histórica (no BackEnd)

Las referencias heredadas a `go`, `cpp`, `java`, `wasm` y `asm` se tratan como inventario histórico o material de migración cerrado. No deben importarse desde `src/pcobra/cobra/transpilers/transpiler/legacy/` ni anunciarse como BackEnd oficial.

## Nota de migración para referencias antiguas

Si un usuario encuentra referencias antiguas a Go, C++, Java, WASM o ASM, debe interpretarlas como documentación histórica o como material de migración, no como targets disponibles del BackEnd oficial. La migración debe hacerse hacia uno de los tres targets oficiales (`python`, `javascript`, `rust`) o hacia la interfaz pública Cobra cuando el target concreto no sea relevante para el usuario final.

## Criterio de salida

Cualquier API pública, CLI pública o documentación orientada a usuario **solo puede listar 3 targets** y deben ser exactamente:

`python`, `javascript`, `rust`.
