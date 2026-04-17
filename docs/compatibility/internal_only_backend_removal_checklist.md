# Checklist de eliminación final por fases (targets internal-only)

Backends en retiro interno: `go`, `cpp`, `java`, `wasm`, `asm`.

**Modo de compatibilidad temporal:** `legacy mode` (`--legacy-targets` o `COBRA_LEGACY_TARGETS_MODE=1`).

**Fecha de retiro total (freeze + eliminación de hooks no usados):** **2027-06-30**.

## Fase 1 — Documentación pública

- [ ] El README público solo sugiere `python`, `javascript`, `rust` como elección de usuario.
- [ ] Las guías públicas eliminan ejemplos de uso directo `--backend go/cpp/java/wasm/asm`.
- [ ] Se conserva únicamente documentación de migración/compatibilidad para targets internal-only.
- [ ] Se ejecuta inventario: `python scripts/ci/generate_internal_only_inventory.py` y se revisa `docs/compatibility/internal_only_refs_inventory.md`.

## Fase 2 — CLI pública

- [ ] El help público oculta targets internal-only por defecto.
- [ ] Cualquier ejecución de targets internal-only falla fuera de `legacy mode` en Fase 2.
- [ ] Los warnings incluyen destino público recomendado y estado de retiro.
- [ ] La telemetría de uso legacy se mantiene habilitada para trazabilidad de migración.

## Fase 3 — Hooks internos no usados

- [ ] Identificar hooks/adaptadores legacy sin uso real (basado en telemetría + CI).
- [ ] Eliminar entradas legacy del registro interno una vez sin tráfico.
- [ ] Eliminar flags de compatibilidad (`COBRA_INTERNAL_LEGACY_TARGETS`, `COBRA_LEGACY_TARGETS_MODE`) al cierre.
- [ ] Ejecutar auditoría final del repositorio y bloquear reintroducciones en CI.

## Criterio de salida

La eliminación se considera completada cuando:

1. La documentación pública no sugiere targets internal-only como opción de usuario.
2. La CLI pública no permite esos targets fuera de `legacy mode`.
3. No quedan hooks legacy activos ni referencias operativas fuera de histórico/migración.
