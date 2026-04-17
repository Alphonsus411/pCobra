# Inventario de referencias internal-only (go/cpp/java/wasm/asm)

Este reporte se genera con `scripts/ci/generate_internal_only_inventory.py`.

## Método

1. **Búsqueda por path**: se recorren archivos de texto fuera de rutas internas permitidas.
2. **Búsqueda por símbolos**: detección de tokens directos, flags (`--backend`/`--tipo`) y claves de registro.

## Rutas internas excluidas

- `src/pcobra/cobra/cli/internal_compat/`
- `docs/compatibility/`
- `docs/historico/`
- `docs/migracion_targets_retirados.md`
- `docs/migracion_cli_unificada.md`
- `tests/`

## Resumen

- Hallazgos fuera de rutas internas: **724**.
- Archivos afectados: **103**.

### Hallazgos por símbolo

- `backend_flag`: 0
- `registry_key`: 0
- `target_token`: 724

### Top paths con más hallazgos

| path | hallazgos |
|---|---:|
| `data/language_equivalence.yml` | 82 |
| `src/pcobra/cobra/transpilers/compatibility_matrix.py` | 47 |
| `docs/contrato_runtime_holobit.md` | 36 |
| `data/language_equivalence_baseline.yml` | 35 |
| `src/pcobra/cobra/transpilers/common/utils.py` | 32 |
| `src/pcobra/cobra/qa/syntax_validation.py` | 24 |
| `docs/proposals/plan_nuevas_funcionalidades.md` | 23 |
| `data/language_equivalence_backlog.md` | 22 |
| `src/pcobra/cobra/benchmarks/targets_policy.py` | 19 |
| `src/pcobra/cobra/transpilers/library_compatibility.py` | 17 |
| `scripts/generar_matriz_transpiladores.py` | 15 |
| `src/pcobra/cobra/transpilers/target_utils.py` | 14 |
| `CONTRIBUTING.md` | 13 |
| `pcobra.toml` | 13 |
| `docs/library_compatibility_matrix.md` | 12 |
| `docs/frontend/backends.rst` | 11 |
| `docs/frontend/transpilers_tier_plan.md` | 11 |
| `docs/_generated/runtime_api_matrix.json` | 10 |
| `docs/_generated/runtime_api_matrix.md` | 10 |
| `scripts/audit_retired_targets.py` | 10 |
| `src/pcobra/cobra/architecture/backend_policy.py` | 10 |
| `src/pcobra/cobra/semantico/cobra_mod_schema.yaml` | 10 |
| `src/pcobra/corelibs/__init__.py` | 9 |
| `docs/frontend/avances.rst` | 8 |
| `src/pcobra/core/sandbox.py` | 8 |

### Muestra de hallazgos

| path | línea | símbolo | extracto |
|---|---:|---|---|
| `CHANGELOG.md` | 17 | `target_token` | `- Migración recomendada: normalizar todo a nombres canónicos (`python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java`, `asm`) en scripts, docs y pipelines.` |
| `CONTRIBUTING.md` | 142 | `target_token` | `- Go` |
| `CONTRIBUTING.md` | 144 | `target_token` | `- Java (`javac`)` |
| `CONTRIBUTING.md` | 163 | `target_token` | `- [ ] No se añadieron referencias a targets fuera de la política oficial (`python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java`, `asm`).` |
| `CONTRIBUTING.md` | 164 | `target_token` | `- [ ] No se añadieron referencias de `transpilar-inverso` fuera de los orígenes oficiales (`python`, `javascript`, `java`).` |
| `CONTRIBUTING.md` | 175 | `target_token` | `- `wasm`` |
| `CONTRIBUTING.md` | 176 | `target_token` | `- `go`` |
| `CONTRIBUTING.md` | 177 | `target_token` | `- `cpp`` |
| `CONTRIBUTING.md` | 178 | `target_token` | `- `java`` |
| `CONTRIBUTING.md` | 179 | `target_token` | `- `asm`` |
| `CONTRIBUTING.md` | 183 | `target_token` | `- **Tier 1**: `python`, `rust`, `javascript`, `wasm`.` |
| `CONTRIBUTING.md` | 184 | `target_token` | `- **Tier 2**: `go`, `cpp`, `java`, `asm`.` |
| `CONTRIBUTING.md` | 190 | `target_token` | `- `java`` |
| `CONTRIBUTING.md` | 242 | `target_token` | `1. Set canónico de targets oficiales (`python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java`, `asm`).` |
| `README.md` | 314 | `target_token` | `Las rutas legacy/internal (`go`, `cpp`, `java`, `wasm`, `asm`) se mantienen fuera de la interfaz pública y solo como soporte transitorio para migración técnica.` |
| `README.md` | 327 | `target_token` | `- **Fase 1 (default):** warning + telemetría cuando se usan `wasm`, `go`, `cpp`, `java` o `asm`.` |
| `README.md` | 995 | `target_token` | `- **Orígenes reverse de entrada**: `python`, `javascript`, `java`.` |
| `README.md` | 997 | `target_token` | `Los nombres `python`, `javascript` y `java` aparecen en ambas listas, pero con papeles distintos: como `--origen` describen **entradas aceptadas** por la ruta reverse; como `--destino` vuelven a significar **targets oficiales de salida ya existentes**. La capacidad reverse no añade targets nuevos ni amplía la lista oficial de salida.` |
| `README.md` | 1095 | `target_token` | `- Go (`golang-go`) para pruebas internas legacy` |
| `README.md` | 1097 | `target_token` | `- Java (`default-jdk`)` |
| `data/language_equivalence.yml` | 7 | `target_token` | `- go` |
| `data/language_equivalence.yml` | 8 | `target_token` | `- cpp` |
| `data/language_equivalence.yml` | 9 | `target_token` | `- java` |
| `data/language_equivalence.yml` | 10 | `target_token` | `- wasm` |
| `data/language_equivalence.yml` | 11 | `target_token` | `- asm` |
| `data/language_equivalence.yml` | 46 | `target_token` | `go:` |
| `data/language_equivalence.yml` | 57 | `target_token` | `cpp:` |
| `data/language_equivalence.yml` | 69 | `target_token` | `java:` |
| `data/language_equivalence.yml` | 81 | `target_token` | `wasm:` |
| `data/language_equivalence.yml` | 91 | `target_token` | `asm:` |
| `data/language_equivalence.yml` | 99 | `target_token` | `- '; backend asm: imports de runtime administrados externamente'` |
| `data/language_equivalence.yml` | 105 | `target_token` | `go: full` |
| `data/language_equivalence.yml` | 106 | `target_token` | `cpp: partial` |
| `data/language_equivalence.yml` | 107 | `target_token` | `java: partial` |
| `data/language_equivalence.yml` | 108 | `target_token` | `wasm: partial` |
| `data/language_equivalence.yml` | 109 | `target_token` | `asm: partial` |
| `data/language_equivalence.yml` | 114 | `target_token` | `go: full` |
| `data/language_equivalence.yml` | 115 | `target_token` | `cpp: partial` |
| `data/language_equivalence.yml` | 116 | `target_token` | `java: partial` |
| `data/language_equivalence.yml` | 117 | `target_token` | `wasm: partial` |
| `data/language_equivalence.yml` | 118 | `target_token` | `asm: partial` |
| `data/language_equivalence.yml` | 123 | `target_token` | `go: full` |
| `data/language_equivalence.yml` | 124 | `target_token` | `cpp: partial` |
| `data/language_equivalence.yml` | 125 | `target_token` | `java: partial` |
| `data/language_equivalence.yml` | 126 | `target_token` | `wasm: partial` |
| `data/language_equivalence.yml` | 127 | `target_token` | `asm: partial` |
| `data/language_equivalence.yml` | 132 | `target_token` | `go: full` |
| `data/language_equivalence.yml` | 133 | `target_token` | `cpp: partial` |
| `data/language_equivalence.yml` | 134 | `target_token` | `java: partial` |
| `data/language_equivalence.yml` | 135 | `target_token` | `wasm: partial` |
| `data/language_equivalence.yml` | 136 | `target_token` | `asm: partial` |
| `data/language_equivalence.yml` | 141 | `target_token` | `go: full` |
| `data/language_equivalence.yml` | 142 | `target_token` | `cpp: partial` |
| `data/language_equivalence.yml` | 143 | `target_token` | `java: partial` |
| `data/language_equivalence.yml` | 144 | `target_token` | `wasm: partial` |
| `data/language_equivalence.yml` | 145 | `target_token` | `asm: partial` |
| `data/language_equivalence.yml` | 150 | `target_token` | `go: full` |
| `data/language_equivalence.yml` | 151 | `target_token` | `cpp: partial` |
| `data/language_equivalence.yml` | 152 | `target_token` | `java: partial` |
| `data/language_equivalence.yml` | 153 | `target_token` | `wasm: partial` |
| `data/language_equivalence.yml` | 154 | `target_token` | `asm: partial` |
| `data/language_equivalence.yml` | 159 | `target_token` | `go: full` |
| `data/language_equivalence.yml` | 160 | `target_token` | `cpp: partial` |
| `data/language_equivalence.yml` | 161 | `target_token` | `java: partial` |
| `data/language_equivalence.yml` | 162 | `target_token` | `wasm: partial` |
| `data/language_equivalence.yml` | 163 | `target_token` | `asm: partial` |
| `data/language_equivalence.yml` | 168 | `target_token` | `go: full` |
| `data/language_equivalence.yml` | 169 | `target_token` | `cpp: partial` |
| `data/language_equivalence.yml` | 170 | `target_token` | `java: partial` |
| `data/language_equivalence.yml` | 171 | `target_token` | `wasm: partial` |
| `data/language_equivalence.yml` | 172 | `target_token` | `asm: partial` |
| `data/language_equivalence.yml` | 177 | `target_token` | `go: full` |
| `data/language_equivalence.yml` | 178 | `target_token` | `cpp: partial` |
| `data/language_equivalence.yml` | 179 | `target_token` | `java: partial` |
| `data/language_equivalence.yml` | 180 | `target_token` | `wasm: partial` |
| `data/language_equivalence.yml` | 181 | `target_token` | `asm: partial` |
| `data/language_equivalence.yml` | 230 | `target_token` | `go:` |
| `data/language_equivalence.yml` | 244 | `target_token` | `cpp:` |
| `data/language_equivalence.yml` | 256 | `target_token` | `java:` |
| `data/language_equivalence.yml` | 268 | `target_token` | `wasm:` |

## Nota de uso

Este inventario es de diagnóstico. La eliminación se ejecuta por fases según `docs/compatibility/internal_only_backend_removal_checklist.md`.

## Clasificación operativa por fase (sin borrado físico anticipado)

- **Fase 1 (ocultar de UX pública):** `asm`.
- **Fase 2 (bloqueo fuera de profile development):** `go`, `cpp`, `java`, `wasm`.
- **Fase 3 (eliminar código/tests internos expirados):** aplicar solo al vencer ventana por backend.
