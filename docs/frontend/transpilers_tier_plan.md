# Plan de implementación por tiers de transpilación (pCobra)

## Objetivo

Dejar por escrito un estado **realista y verificable** del frente de transpilación actual de pCobra, separando cuatro bloques de seguimiento:

1. registro canónico de targets,
2. limpieza legacy,
3. compatibilidad Holobit/runtime,
4. tooling de ejecución.

Los tiers oficiales siguen siendo:

- **Tier 1:** `python`, `rust`, `javascript`, `wasm`.
- **Tier 2:** `go`, `cpp`, `java`, `asm`.

> Este documento ya no debe leerse como “todo completado”, sino como una hoja de seguimiento basada en el estado real del código a fecha de revisión.

## Bloque 1 — Registro canónico de targets

**Estado actual:** en gran parte resuelto, con validaciones automáticas claras.

**Archivos vinculados**
- `src/pcobra/cobra/transpilers/targets.py`
- `src/pcobra/cobra/transpilers/registry.py`
- `src/pcobra/cobra/transpilers/compatibility_matrix.py`
- `src/pcobra/cobra/cli/commands/compile_cmd.py`

**Seguimiento realista**
- [x] Existe una fuente de verdad para los nombres canónicos y los tiers en `targets.py`.
- [x] El registro canónico de clases (`registry.py`) expone exactamente 8 backends oficiales.
- [x] `LANG_CHOICES` deriva del registro oficial y la CLI valida nombres canónicos.
- [x] La matriz contractual (`compatibility_matrix.py`) cubre exclusivamente los 8 targets oficiales y valida su propia forma.
- [ ] Sigue pendiente simplificar mensajes, documentación y ayudas para que toda la terminología pública dependa de una única ruta de política, sin duplicidades entre CLI y documentación.

## Bloque 2 — Limpieza legacy

**Estado actual:** avanzada, pero no cerrada al 100 % si se exige ausencia total de compatibilidades históricas internas.

**Archivos vinculados**
- `src/pcobra/cobra/transpilers/module_map.py`
- `src/pcobra/cobra/transpilers/registry.py`
- `src/pcobra/cobra/transpilers/targets.py`
- `scripts/ci/validate_targets.py`
- `tests/unit/test_cli_target_aliases.py`

**Seguimiento realista**
- [x] El árbol principal de transpiladores `to_*.py` ya está recortado a los 8 backends oficiales.
- [x] La CLI pública rechaza aliases legacy como `js` o `ensamblador`.
- [x] Existe una auditoría automática para detectar aliases legacy y módulos fuera de política.
- [x] `module_map.py` ya resuelve solo desde `cobra.toml` con `[modulos."..."]` y los 8 nombres canónicos de `OFFICIAL_TARGETS`.
- [ ] La limpieza legacy sigue siendo parcial mientras persistan excepciones internas/históricas de compatibilidad y validadores específicos para rutas heredadas.
- [ ] No hay evidencia en esta revisión de que se hayan eliminado todos los “nodos específicos” históricos fuera de alcance; ese punto requiere auditoría dirigida adicional si se quiere marcar como completado.

## Bloque 3 — Compatibilidad Holobit/runtime

**Estado actual:** existe contrato explícito, pero el soporte es desigual por backend y no debe presentarse como paridad funcional total.

**Archivos vinculados**
- `src/pcobra/cobra/transpilers/compatibility_matrix.py`
- `src/pcobra/cobra/transpilers/targets.py`
- `src/pcobra/cobra/transpilers/module_map.py`
- `pyproject.toml`
- `tests/integration/test_holobit_tiers.py`
- `tests/integration/transpilers/test_official_backends_contracts.py`
- `tests/integration/transpilers/test_official_backends_tier1.py`
- `tests/integration/transpilers/test_official_backends_tier2.py`

**Seguimiento realista**
- [x] Hay una matriz contractual pública por backend y feature (`holobit`, `proyectar`, `transformar`, `graficar`, `corelibs`, `standard_library`).
- [x] Python figura como `full` en todas las features del contrato actual.
- [x] JavaScript figura como `full` para primitivas Holobit y `partial` para `corelibs`/`standard_library`.
- [x] Rust, WASM, Go, C++, Java y ASM están declarados explícitamente como `partial` en la matriz actual.
- [x] Existen suites contractuales por tier y una suite consolidada por backend/feature.
- [ ] Las suites contractuales no deben darse por totalmente cerradas: en la revisión actual siguen apareciendo desajustes puntuales entre expectativas y codegen real en algunos backends/features parciales.
- [ ] El proyecto no garantiza ejecución end-to-end homogénea para los 8 backends: fuera de Python y JavaScript la evidencia principal es de **codegen contractual**, no de runtime completo.
- [ ] El runtime JavaScript sigue dependiendo de prerrequisitos externos del entorno (`node`, `vm2`, y en algunos casos `node-fetch`), así que no debe describirse como garantía incondicional.
- [ ] La dependencia `holobit-sdk` está declarada en `pyproject.toml` solo para Python `>=3.10`; la documentación no debe presentar su disponibilidad como universal ni incondicional.

## Bloque 4 — Tooling de ejecución

**Estado actual:** separado de la transpilación, con alcance mucho más reducido.

**Archivos vinculados**
- `src/pcobra/core/sandbox.py`
- `src/pcobra/cobra/cli/target_policies.py`
- `Makefile`
- `pyproject.toml`
- `.github/workflows/test.yml`
- `.github/workflows/ci.yml`

**Seguimiento realista**
- [x] La política de CLI separa targets oficiales de transpilación y targets oficiales con runtime.
- [x] `sandbox.py` documenta y aplica soporte de ejecución en contenedor solo para `python`, `javascript`, `cpp` y `rust`.
- [x] `Makefile` construye contenedores oficiales únicamente para esos cuatro runtimes.
- [x] La CI ejecuta suites contractuales bloqueantes para los backends oficiales.
- [ ] `make test` y `make check` no expresan por sí solos una matriz de ejecución por backend; esa separación vive principalmente en tests específicos y workflows.
- [ ] `go`, `java`, `wasm` y `asm` siguen siendo targets oficiales de generación, pero no deben documentarse como runtimes Docker/sandbox equivalentes.

## Criterios de aceptación verificables

### A. Registro canónico de targets

1. `OFFICIAL_TARGETS`, el registro de transpiladores y `LANG_CHOICES` permanecen alineados.
2. La matriz contractual define exactamente los 8 backends oficiales.

**Comprobaciones sugeridas**

```bash
python -m pytest tests/unit/test_official_targets_consistency.py
python -m pytest tests/unit/test_compile_cmd_target_choices_aliases.py
python -m pytest tests/unit/test_holobit_backend_contract_matrix.py
```

### B. Limpieza legacy

1. No aparecen menciones a orígenes reverse retirados en rutas públicas actuales.
2. No existen módulos `to_*.py` fuera del alcance oficial.
3. La CLI pública rechaza aliases legacy (`js`, `ensamblador`, etc.).
4. No hay aliases legacy en código productivo expuesto por la política pública.

**Comprobaciones sugeridas**

```bash
python scripts/ci/validate_targets.py
find src/pcobra/cobra/transpilers/transpiler -maxdepth 1 -name 'to_*.py' | sort
python -m pytest tests/unit/test_cli_target_aliases.py
python scripts/ci/validate_targets.py
```

### C. Igualdad entre contrato y matrix

1. La suite por tier valida que cada backend respeta el nivel declarado en `compatibility_matrix.py`.
2. La validación estructural del contrato no detecta regresiones por debajo del mínimo requerido.

**Comprobaciones sugeridas**

```bash
python -m pytest tests/integration/transpilers/test_official_backends_tier1.py
python -m pytest tests/integration/transpilers/test_official_backends_tier2.py
python -m pytest tests/unit/test_holobit_backend_contract_matrix.py
```

### D. Suites contractuales por backend

1. La suite consolidada por backend/feature transpila los 8 backends oficiales.
2. Python debe ejecutar el programa generado en el runtime del repositorio.
3. JavaScript solo se considera ejecutable cuando el entorno dispone de `node` y dependencias runtime.

**Comprobaciones sugeridas**

```bash
python -m pytest tests/integration/transpilers/test_official_backends_contracts.py
python -m pytest tests/integration/test_holobit_tiers.py
```

## Matriz mínima contractual vigente

> La matriz contractual vigente es la de `src/pcobra/cobra/transpilers/compatibility_matrix.py`. Se resume aquí sin prometer más de lo que hoy valida el código.

| Backend | Tier | holobit | proyectar | transformar | graficar | corelibs | standard_library |
|---|---|---|---|---|---|---|---|
| `python` | Tier 1 | full | full | full | full | full | full |
| `javascript` | Tier 1 | partial | partial | partial | partial | partial | partial |
| `rust` | Tier 1 | partial | partial | partial | partial | partial | partial |
| `wasm` | Tier 1 | partial | partial | partial | partial | partial | partial |
| `go` | Tier 2 | partial | partial | partial | partial | partial | partial |
| `cpp` | Tier 2 | partial | partial | partial | partial | partial | partial |
| `java` | Tier 2 | partial | partial | partial | partial | partial | partial |
| `asm` | Tier 2 | partial | partial | partial | partial | partial | partial |

## Nota de interpretación

- **`full`** significa contrato cubierto por regresión de generación y símbolos/hooks esperados.
- **`partial`** significa generación contractual con fallback o error explícito, no equivalencia funcional total con Python.
- El hecho de que un backend sea oficial para **transpilación** no implica que tenga runtime Docker/sandbox oficial ni ejecución automática en todas las suites.
