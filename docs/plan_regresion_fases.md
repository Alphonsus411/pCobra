# Plan de regresión por fases

Este documento define un plan **determinista y verificable** de regresión para 5 fases. Incluye:

- Matriz por fase con artefactos, pruebas y evidencia.
- Paquete mínimo de regresión por fase.
- Checklist de cierre (DoD) con criterios objetivos.

## 1) Matriz de regresión por fase

| Fase | Archivos tocados (esperados) | Tests nuevos | Regresiones ejecutadas | Criterio exacto de aceptación | Evidencia (salida/resumen) |
|---|---|---|---|---|---|
| **Fase 1**: Startup policy + targets públicos | `src/cli/**`, `src/core/**`, `docs/architecture/**`, `scripts/ci/**` | `tests/test_backend_startup_policy.py`, `tests/cli/test_public_v2_commands_contract.py`, `tests/unit/test_public_command_policy.py`, `tests/integration/test_cli_public_help_contract.py` | `python -m pytest -q tests/test_backend_startup_policy.py tests/cli/test_public_v2_commands_contract.py tests/unit/test_public_command_policy.py tests/integration/test_cli_public_help_contract.py`, smoke: `python -m pcobra --help` | (1) La policy de startup rechaza configuraciones inválidas con código de salida `!=0` y mensaje estable. (2) Los targets públicos listados coinciden exactamente con el contrato documentado. | Log de tests con `ok` en todos los casos + snapshot del listado de targets públicos + salida de `--help` con versión/uso esperados. |
| **Fase 2**: Contrato `usar` + seguridad de resolución | `src/core/resolver/**`, `src/core/parser/**`, `src/cli/**`, `docs/standard_library/**` | `tests/integration/test_usar_core_contract_full.py`, `tests/unit/test_project_root_usar_resolution.py`, `tests/integration/test_usar_project_modules.py` | `python -m pytest -q tests/integration/test_usar_core_contract_full.py tests/unit/test_project_root_usar_resolution.py tests/integration/test_usar_project_modules.py` | (1) `usar` solo acepta rutas/aliases del contrato. (2) Resolución bloquea path traversal y referencias fuera de raíz permitida. (3) Errores son deterministas (mismo código y mensaje normalizado). | Reporte de casos válidos/ inválidos con conteo exacto (p.ej. 12/12) + evidencia de rechazo de `../` y rutas absolutas no permitidas. |
| **Fase 3**: Snapshots de exportación | `src/bindings/**`, `src/pcobra/**`, `docs/compatibility/**`, `docs/_generated/**` | `tests/test_usar_public_exports_snapshot.py`, `tests/unit/test_corelibs_surface_exports.py`, `tests/unit/test_targets_docs_generated_blocks_snapshot.py` + snapshots versionados | `python -m pytest -q tests/test_usar_public_exports_snapshot.py tests/unit/test_corelibs_surface_exports.py tests/unit/test_targets_docs_generated_blocks_snapshot.py` | (1) Exportaciones coinciden byte a byte con snapshots aprobados. (2) Si hay cambio, requiere actualización explícita de snapshot + revisión humana. | Diff de snapshot en `0` cambios para rama estable o diff intencional aprobado con hash/commit asociado. |
| **Fase 4**: Contrato Holobit + no-fuga SDK | `src/bindings/holobit/**`, `src/core/sdk/**`, `docs/architecture/**`, `docs/proposals/**` | `tests/integration/test_holobit_tiers.py`, `tests/unit/test_holobit_no_fuga_exports.py`, `tests/unit/test_holobit_backend_contract_matrix.py` | `python -m pytest -q tests/integration/test_holobit_tiers.py tests/unit/test_holobit_no_fuga_exports.py tests/unit/test_holobit_backend_contract_matrix.py`, `rg "internal::|experimental::" src/pcobra -n` sobre API pública | (1) Interfaz Holobit cumple campos, tipos y semántica pactada. (2) API pública no expone símbolos internos de SDK (no-fuga). | Acta de contrato (campos esperados vs reales) + salida de prueba de no-fuga (`0` coincidencias prohibidas). |
| **Fase 5**: Validaciones CI obligatorias | `.github/workflows/**` o `scripts/ci/**`, `Makefile`/`justfile`, `docs/ADR/**` | `tests/ci_required_checks/*` (si aplica) | `python -m pytest -q tests/test_workflows_yaml.py tests/test_codeql_config.py tests/test_tooling_excludes.py`, `python -m pytest -q` como suite general razonable | (1) Checks obligatorios definidos y bloqueantes para merge. (2) Mapeo 1:1 entre CI y comando local reproducible. (3) Cualquier fallo detiene promoción. | URL/ID de pipeline verde + tabla de correspondencia `check CI -> comando local` + evidencia de política de branch protection. |

---

## 2) Paquete mínimo de regresión por fase

> Ejecutar siempre en entorno limpio y versionado (`git clean -xfd` opcional en CI), con versión fija de toolchain.

### Fase 1 — Startup policy + targets públicos

1. Verificar arranque y CLI básica.
2. Validar catálogo de targets públicos.
3. Confirmar errores deterministas en startup inválido.

**Comandos base (referenciales):**

```bash
python -m pytest -q tests/test_backend_startup_policy.py \
  tests/cli/test_public_v2_commands_contract.py \
  tests/unit/test_public_command_policy.py \
  tests/integration/test_cli_public_help_contract.py
python -m pcobra --help
```

### Fase 2 — Contrato `usar` + seguridad de resolución

1. Casos felices del contrato `usar`.
2. Casos de rechazo (`../`, rutas absolutas, alias inválidos, ciclos).
3. Validar códigos y mensajes estables.

**Comandos base (referenciales):**

```bash
python -m pytest -q tests/integration/test_usar_core_contract_full.py \
  tests/unit/test_project_root_usar_resolution.py \
  tests/integration/test_usar_project_modules.py
```

### Fase 3 — Snapshots de exportación

1. Generar exportaciones deterministas.
2. Comparar contra baseline versionado.
3. Fallar si hay drift sin aprobación.

**Comandos base (referenciales):**

```bash
python -m pytest -q tests/test_usar_public_exports_snapshot.py \
  tests/unit/test_corelibs_surface_exports.py \
  tests/unit/test_targets_docs_generated_blocks_snapshot.py
```

### Fase 4 — Contrato Holobit + no-fuga SDK

1. Validar esquema del contrato Holobit.
2. Verificar que API pública no expone internals.
3. Confirmar compatibilidad con consumidores externos.

**Comandos base (referenciales):**

```bash
python -m pytest -q tests/integration/test_holobit_tiers.py \
  tests/unit/test_holobit_no_fuga_exports.py \
  tests/unit/test_holobit_backend_contract_matrix.py
rg "internal::|experimental::" src/pcobra -n
```

### Fase 5 — Validaciones CI obligatorias

1. Ejecutar suite local equivalente a CI.
2. Verificar checks requeridos en pipeline.
3. Confirmar bloqueo de merge ante fallo.

**Comandos base (referenciales):**

```bash
python -m pytest -q tests/test_workflows_yaml.py \
  tests/test_codeql_config.py \
  tests/test_tooling_excludes.py
python -m pytest -q
```

---

## 3) Checklist de cierre por fase (DoD)

### DoD Fase 1

- [ ] Casos de startup policy cubren válidos e inválidos críticos.
- [ ] Targets públicos documentados = targets públicos probados.
- [ ] Evidencia adjunta: logs + resumen con versión de toolchain.
- [ ] Re-ejecución en limpio produce mismo resultado.

### DoD Fase 2

- [ ] Contrato `usar` validado en parser + resolver.
- [ ] Pruebas de seguridad de resolución cubren traversal y escapes de raíz.
- [ ] Errores normalizados (código/mensaje) sin ambigüedad.
- [ ] Evidencia repetible con conteo de pruebas y semilla/entorno fijo.

### DoD Fase 3

- [ ] Snapshots versionados y revisados.
- [ ] No hay drift no justificado en exportación.
- [ ] Cambios intencionales de snapshot incluyen racional técnico.
- [ ] Evidencia incluye diff o confirmación de 0 cambios.

### DoD Fase 4

- [ ] Contrato Holobit pasa validación estructural y semántica.
- [ ] Prueba de no-fuga SDK pasa con 0 símbolos prohibidos expuestos.
- [ ] Compatibilidad externa verificada con fixture/consumer de referencia.
- [ ] Evidencia trazable a commit y job CI.

### DoD Fase 5

- [ ] Todos los checks obligatorios están declarados como requeridos.
- [ ] Existe comando local equivalente para cada check CI.
- [ ] Rama protegida impide merge con checks en rojo.
- [ ] Evidencia incluye pipeline verde + tabla de trazabilidad CI/local.

---

## 4) Regla de aceptación global

Se considera aceptada una fase **solo si**:

1. Tiene evidencia verificable de cumplimiento, específica y sin ambigüedad.
2. La validación puede repetirse de forma determinista por cualquier miembro del equipo.
3. El resultado queda trazado a commit, versión de toolchain y comando ejecutado.

## 5) Plantilla de evidencia por fase (recomendada)

Usar este formato en PR/issue de cierre de fase:

```md
### Evidencia Fase X
- Commit: <hash>
- Entorno: <OS/toolchain>
- Comandos ejecutados:
  - <comando 1>
  - <comando 2>
- Resultado:
  - Tests: <N pasados, 0 fallos>
  - Regresión: <pass/fail>
- Artefactos:
  - <ruta log/snapshot/reporte>
- Observaciones:
  - <riesgos/decisiones>
```
