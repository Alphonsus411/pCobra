# Inventario operativo de backends (Tier 1/Tier 2)

Fecha de corte: **2026-03-28**.

Este inventario consolida el estado real del árbol activo para cumplir el cierre de limpieza:

1. inventario de `codegen/`, `transpilers/`, `emitters/`, plugins y adaptadores,
2. eliminación de cualquier backend fuera de Tier 1/Tier 2,
3. limpieza de referencias colgantes,
4. guardrails para impedir registros fuera de la matriz oficial.

## Matriz oficial vigente

- **Tier 1**: `python`, `rust`, `javascript`, `wasm`.
- **Tier 2**: `go`, `cpp`, `java`, `asm`.
- **Únicos targets oficiales**: exactamente 8 (`OFFICIAL_TARGETS = Tier1 + Tier2`).

## 1) Inventario de backends activos por categoría

### A. `transpilers/` (productivo)

- `src/pcobra/cobra/transpilers/transpiler/to_python.py`
- `src/pcobra/cobra/transpilers/transpiler/to_rust.py`
- `src/pcobra/cobra/transpilers/transpiler/to_js.py`
- `src/pcobra/cobra/transpilers/transpiler/to_wasm.py`
- `src/pcobra/cobra/transpilers/transpiler/to_go.py`
- `src/pcobra/cobra/transpilers/transpiler/to_cpp.py`
- `src/pcobra/cobra/transpilers/transpiler/to_java.py`
- `src/pcobra/cobra/transpilers/transpiler/to_asm.py`

### B. `codegen/` y `emitters/`

- No hay directorios productivos `codegen/` ni `emitters/` en el árbol activo.
- Se consideran rutas legacy retiradas y ahora quedan cubiertas por auditoría CI explícita.

### C. Plugins / adaptadores

- Entrada de plugins de transpilers: grupo `entry_points("cobra.transpilers")`.
- Registro canónico en runtime: `TRANSPILER_CLASS_PATHS`.
- Política: sólo se aceptan nombres canónicos oficiales (sin aliases ni targets extra).

## 2) Backends fuera de Tier 1/Tier 2

No hay módulos `to_*.py` fuera del set oficial ni carpetas `*_nodes` extra en el árbol productivo.

## 3) Limpieza de artefactos colaterales

- No hay fixtures/goldens oficiales fuera de los 8 targets canónicos.
- No hay flags CLI públicas fuera del set canónico (`LANG_CHOICES` se deriva del registro oficial).

## 4) Limpieza de referencias colgantes (registries / dispatch / DI)

- `TRANSPILER_CLASS_PATHS` valida exactitud (claves, cardinalidad y orden) frente a `OFFICIAL_TARGETS`.
- `compile_cmd.register_transpiler_backend(...)` y `_validate_entrypoint_backend_or_raise(...)`
  rechazan targets fuera de matriz oficial.

## 5) Búsqueda textual de residuos legacy

Se ejecutó búsqueda textual sobre:

- nombres de lenguajes retirados (según política CI del repositorio);
- rutas antiguas de backend y namespaces históricos de transpilación.

Resultado: sin referencias activas en rutas productivas del árbol.

## 6) Verificación de fallo al registrar backend fuera de matriz oficial

Cobertura de guardrail:

- `tests/unit/test_compile_backend_registration.py` (rechazo en registro y entrypoints);
- `tests/unit/test_registry_contract_guardrail.py` (falla de contrato si el registro canónico
  incluye un target extra o pierde uno oficial).

Con esto, una desviación del registro fuera de la matriz oficial rompe validaciones/tests de contrato.
