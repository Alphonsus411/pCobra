# Plan operativo por tiers de transpilación (pCobra)

## Objetivo

Definir el estado vigente de transpilación sin ambigüedades, con una separación normativa clara entre:

1. targets oficiales de salida,
2. runtime oficial,
3. runtime best-effort,
4. targets solo de transpilación,
5. alcance SDK full.

## Tiers oficiales (salida)

- **Tier 1:** `python`, `rust`, `javascript`, `wasm`.
- **Tier 2:** `go`, `cpp`, `java`, `asm`.

La unión de ambos tiers es el set oficial de salida de 8 backends.

## Contrato vigente por categoría

- **Targets oficiales de salida (8):** `python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java`, `asm`.
- **Runtime oficial verificable:** `python`, `rust`, `javascript`, `cpp`.
- **Runtime best-effort:** `go`, `java`.
- **Solo transpilación:** `wasm`, `asm`.
- **SDK full:** solo `python`.

Ninguna categoría fuera de `python` puede documentarse como compatibilidad SDK completa.
En particular, **javascript figura como `partial`** en el contrato vigente.

## Fuente canónica

**Archivos vinculados**
- `src/pcobra/cobra/transpilers/targets.py`
- `src/pcobra/cobra/transpilers/registry.py`
- `src/pcobra/cobra/transpilers/compatibility_matrix.py`
- `src/pcobra/cobra/cli/target_policies.py`
- `src/pcobra/cobra/cli/commands/compile_cmd.py`

## Reglas de documentación pública

1. Usar únicamente los 8 nombres canónicos de backend.
2. No publicar aliases no oficiales en ejemplos de CLI.
3. En CLI, usar nomenclatura canónica de opciones: `--backend`, `--tipo`, `--tipos`.
4. Distinguir de forma explícita salida, runtime oficial, best-effort, solo transpilación y alcance SDK full.
5. No mezclar el alcance reverse (`cobra transpilar-inverso`) con los targets de salida.

## Matriz mínima contractual vigente

| Backend | Tier | Runtime | SDK |
|---|---|---|---|
| `python` | Tier 1 | oficial verificable | full |
| `rust` | Tier 1 | oficial verificable | partial |
| `javascript` | Tier 1 | oficial verificable | partial |
| `wasm` | Tier 1 | solo transpilación | partial |
| `go` | Tier 2 | best-effort | partial |
| `cpp` | Tier 2 | oficial verificable | partial |
| `java` | Tier 2 | best-effort | partial |
| `asm` | Tier 2 | solo transpilación | partial |

## Comprobaciones recomendadas

```bash
python scripts/generate_target_policy_docs.py
python scripts/generar_matriz_transpiladores.py
python scripts/validate_targets_policy.py
python scripts/ci/validate_targets.py
python -m pytest tests/unit/test_official_targets_consistency.py
python -m pytest tests/unit/test_cli_target_aliases.py
```
