# Checklist de eliminación final por fases (targets internal-only)

Backends en retiro interno: `go`, `cpp`, `java`, `wasm`, `asm`.

**Modo de compatibilidad temporal:** `legacy mode` (`--legacy-targets` o `COBRA_LEGACY_TARGETS_MODE=1`).

**Fecha de retiro total (freeze + eliminación de hooks no usados):** **2027-06-30**.

## Fase 1 — Documentación pública

- [ ] El README público solo sugiere `python`, `javascript`, `rust` como elección de usuario.
- [ ] Las guías públicas eliminan ejemplos de uso directo `--backend go/cpp/java/wasm/asm`.
- [ ] Los comandos obsoletos (`dependencias`, `bench*`, `profile`, `transpilar-inverso`, `validar-sintaxis`, `qa-validar`) no aparecen en help/documentación pública.
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

## Priorización explícita de limpieza de transpilers legacy (al vencer ventana)

> **Regla:** no borrar físicamente antes de vencer la ventana de retiro del backend.

1. `src/pcobra/cobra/transpilers/transpiler/to_asm.py` (Q3 2026).
2. `src/pcobra/cobra/transpilers/transpiler/to_go.py` (Q4 2026).
3. `src/pcobra/cobra/transpilers/transpiler/to_cpp.py` (Q4 2026).
4. `src/pcobra/cobra/transpilers/transpiler/to_java.py` (Q1 2027).
5. `src/pcobra/cobra/transpilers/transpiler/to_wasm.py` (Q2 2027).

Para cada backend en ventana vencida:

- [ ] Eliminar código del transpilador y nodos asociados.
- [ ] Eliminar tests/unit + tests/integration/goldens expirados del backend.
- [ ] Eliminar hooks internos/registro y referencias operativas restantes.

## Checklist CI — No exposición pública de legacy targets

- [ ] `python scripts/ci/validate_targets.py` incluye gate de **no exposición pública** en superficies help/docs.
- [ ] `tests/integration/test_cli_public_help_contract.py` sigue en verde (sin `go/cpp/java/wasm/asm` en help público).
- [ ] Cualquier hallazgo de exposición pública bloquea merge.

## Criterio de salida

La eliminación se considera completada cuando:

1. La documentación pública no sugiere targets internal-only como opción de usuario.
2. La CLI pública no permite esos targets fuera de `legacy mode`.
3. No quedan hooks legacy activos ni referencias operativas fuera de histórico/migración.
