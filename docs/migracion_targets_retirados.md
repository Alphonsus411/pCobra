# Guía de migración desde targets retirados

Este documento describe cómo migrar proyectos que dependían de targets eliminados del alcance público operativo.

## Estado actual (canónico + deprecaciones activas)

Los targets canónicos públicos de salida registrados por `PUBLIC_BACKENDS` son:

- **Tier 1 público**: `python`, `javascript`, `rust`.
- **Legacy interno/histórico**: `wasm`, `go`, `cpp`, `java`, `asm` quedan fuera de la superficie pública.

### Deprecación pública (2 fases)

Desde esta versión se deprecan en CLI pública los targets:

- `wasm`, `go`, `cpp`, `java`, `asm`.

Plan aplicado:

1. **Fase 1 (actual por defecto)**: warning en CLI + telemetría de uso.
2. **Fase 2**: ocultos del help público y disponibles solo en modo legacy (`--legacy-targets` o `COBRA_LEGACY_TARGETS_MODE=1`).

Si tu flujo usa un target retirado, debes moverlo a uno de los 3 targets públicos: `python`, `javascript` o `rust`.

## Selección de destino recomendada

Elige el target según objetivo de tu pipeline:

1. **Necesitas runtime oficial verificable en CLI/sandbox/contenedor**
   Migra a: `python`, `javascript` o `rust`.
2. **Necesitas salida legacy o artefactos de inspección**
   Mantén ese uso fuera de la CLI/documentación pública y trátalo como migración interna temporal.

## Migración de comandos CLI

1. Sustituye cualquier nombre de target legacy por nombre canónico oficial.
2. Revisa scripts de CI para usar solo:
   - `cobra compilar ... --tipo <target>`
   - `cobra compilar ... --tipos <lista_canónica>`
3. Evita exponer en documentación pública los targets deprecados (`wasm`, `go`, `cpp`, `java`, `asm`) salvo notas de migración/legacy.

## Compatibilidad Holobit SDK y librerías tras migrar

- **Compatibilidad SDK full**: solo `python`.
- **Resto de targets públicos oficiales**: `javascript` y `rust` mantienen compatibilidad `partial`.
- **Soporte oficial de runtime para `corelibs`/`standard_library`**: `python`, `javascript`, `rust`.
- `wasm`, `go`, `cpp`, `java` y `asm`: rutas legacy internas/históricas, sin contrato público.

## Checklist de salida

- [ ] No quedan referencias a targets retirados en documentación pública principal, salvo enlaces explícitos a anexos internos, migración o histórico.
- [ ] Todos los comandos y snippets públicos usan únicamente `python`, `javascript` y `rust`.
- [ ] Se validó documentación y política con:

```bash
python scripts/generate_target_policy_docs.py
python scripts/ci/validate_targets.py
python scripts/ci/ensure_generated_targets_docs_clean.py
```

## Archivo histórico

Para consultar cronologías antiguas de aliases, ejemplos legacy o notas de transición ya cerradas, revisa:

- `docs/historico/migracion_targets_retirados_archivo.md`

Ese material se conserva solo como referencia histórica y no forma parte del flujo operativo activo ni del BackEnd oficial público.
