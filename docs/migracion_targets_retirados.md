# Guía de migración desde targets retirados

Este documento describe cómo migrar proyectos que dependían de targets eliminados del alcance público operativo.

## Estado actual (canónico)

Los únicos targets oficiales de salida son:

- **Tier 1**: `python`, `rust`, `javascript`, `wasm`
- **Tier 2**: `go`, `cpp`, `java`, `asm`

Si tu flujo usa un target retirado, debes moverlo a uno de estos 8.

## Selección de destino recomendada

Elige el target según objetivo de tu pipeline:

1. **Necesitas runtime oficial verificable en CLI/sandbox/contenedor**  
   Migra a: `python`, `rust`, `javascript` o `cpp`.
2. **Necesitas salida oficial pero aceptas runtime best-effort**  
   Migra a: `go` o `java`.
3. **Solo necesitas artefacto de transpilación/inspección**  
   Migra a: `wasm` o `asm`.

## Migración de comandos CLI

1. Sustituye cualquier nombre de target legacy por nombre canónico oficial.
2. Revisa scripts de CI para usar solo:
   - `cobra compilar ... --tipo <target>`
   - `cobra compilar ... --tipos <lista_canónica>`
3. Valida que los ejemplos y documentación no incluyan aliases ni targets retirados.

## Compatibilidad Holobit SDK y librerías tras migrar

- **Compatibilidad SDK full**: solo `python`.
- **Resto de targets oficiales**: compatibilidad `partial`.
- **Soporte oficial de runtime para `corelibs`/`standard_library`**: `python`, `rust`, `javascript`, `cpp`.
- `go`/`java`: runtime best-effort.
- `wasm`/`asm`: solo transpilación.

## Checklist de salida

- [ ] No quedan referencias a targets retirados en `README`, `docs/`, `examples/`, `scripts/`.
- [ ] Todos los comandos y snippets usan únicamente los 8 targets canónicos.
- [ ] Se validó documentación y política con:

```bash
python scripts/generate_target_policy_docs.py
python scripts/ci/validate_targets.py
python scripts/ci/ensure_generated_targets_docs_clean.py
```
