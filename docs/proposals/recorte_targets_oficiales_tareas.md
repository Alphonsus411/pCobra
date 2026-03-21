# Tareas estructuradas para consolidar el recorte de targets oficiales

## Objetivo

Este documento es el **documento madre de implementación** para cerrar el trabajo pendiente tras el recorte ya decidido del alcance oficial.

> **Aclaración de alcance**
>
> El objetivo de esta propuesta **no es cambiar el set de 8 targets oficiales**. Ese recorte ya está resuelto y la fuente de verdad vigente ya fija estos destinos:
>
> - Tier 1: `python`, `rust`, `javascript`, `wasm`
> - Tier 2: `go`, `cpp`, `java`, `asm`
>
> El trabajo pendiente consiste en:
>
> 1. limpiar restos legacy o divergentes en código, tooling, tests y documentación;
> 2. blindar regresiones con validaciones reales del repositorio;
> 3. mantener alineado el contrato Holobit/`corelibs`/`standard_library`;
> 4. evitar que la documentación pública o la CLI vuelvan a sobredimensionar compatibilidad o runtime.

## Documentos normativos que se deben leer antes de implementar

Esta propuesta **no duplica criterios normativos**. Cada ticket debe leerse junto con estos documentos:

- `docs/targets_policy.md`: política oficial de nombres canónicos, tiers, separación entre transpilación y runtime, alcance de CI y reglas de mantenimiento.
- `docs/matriz_transpiladores.md`: matriz contractual mínima por backend/feature y lectura correcta del alcance real.
- `docs/contrato_runtime_holobit.md`: contrato mínimo de hooks/runtime Holobit y obligación de error explícito para backends `partial`.

## Fuente de verdad y validaciones reales del repositorio

Antes de tocar cualquier bloque, el implementador debe asumir esta trazabilidad mínima:

### Código canónico

- `src/pcobra/cobra/transpilers/targets.py`: define `TIER1_TARGETS`, `TIER2_TARGETS`, `OFFICIAL_TARGETS` y helpers canónicos de normalización/ayuda.
- `src/pcobra/cobra/transpilers/registry.py`: registro canónico de clases oficiales y orden exacto del registro.
- `src/pcobra/cobra/cli/target_policies.py`: separación entre targets oficiales de transpilación, runtime oficial, runtime verificable y solo generación.
- `src/pcobra/cobra/transpilers/compatibility_matrix.py`: matriz contractual mínima de Holobit, `corelibs` y `standard_library`.

### Scripts de validación obligatorios

- `scripts/validate_targets_policy.py`: auditoría textual/pública de política de targets y documentación.
- `scripts/ci/validate_targets.py`: validación anti-regresión de registro, árbol `to_*.py` / `from_*.py`, listas públicas, documentación y reverse scope.

### Tests de consistencia y contrato que ya existen

- `tests/unit/test_official_targets_consistency.py`
- `tests/unit/test_cli_target_aliases.py`
- `tests/unit/test_public_docs_scope.py`
- `tests/unit/test_holobit_backend_contract_matrix.py`
- `tests/unit/test_target_execution_policy.py`
- `tests/unit/test_validate_targets_policy_script.py`
- `tests/integration/transpilers/test_official_backends_tier1.py`
- `tests/integration/transpilers/test_official_backends_tier2.py`
- `tests/integration/transpilers/test_official_backends_contracts.py`

## Estado operativo global

- **Estado actual del programa**: en curso.
- **Responsable sugerido**: equipo de transpilers/CLI.
- **Dependencia macro**: no ampliar ni reducir `OFFICIAL_TARGETS`; trabajar sobre limpieza, documentación, tests y validaciones.
- **Criterio global de cierre**: todas las tareas de abajo quedan cerradas con validación automática verde y sin divergencias entre `targets.py`, `registry.py`, `target_policies.py`, `compatibility_matrix.py`, documentación normativa y suites de contrato.

---

## Tickets de implementación

> Convención de estados sugerida por ticket:
>
> - `Pendiente`: sin cambios implementados aún.
> - `En curso`: hay trabajo activo o diff parcial.
> - `Bloqueado`: falta dependencia previa.
> - `Cerrado`: criterio verificable cumplido y pruebas/scripts asociados en verde.

### Ticket A1 — Verificar constantes canónicas y helpers públicos

| Campo | Detalle |
|---|---|
| Estado | Pendiente |
| Responsable sugerido | Equipo transpilers |
| Dependencias | Ninguna; base del resto del bloque A |
| Archivos a revisar | `src/pcobra/cobra/transpilers/targets.py` |
| Archivos relacionados | `src/pcobra/cobra/cli/target_policies.py`, `src/pcobra/cobra/cli/commands/compile_cmd.py`, `tests/utils/targets.py` |
| Validaciones reales | `python -m pytest tests/unit/test_official_targets_consistency.py`; `python -m pytest tests/unit/test_cli_target_aliases.py` |
| Criterio de cierre verificable | `TIER1_TARGETS`, `TIER2_TARGETS`, `OFFICIAL_TARGETS` y helpers públicos aceptan/emiten solo nombres canónicos (`python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java`, `asm`) y no reintroducen aliases legacy en UX pública. |

**Trabajo esperado**

- Confirmar que `normalize_target_name`, `target_cli_choices`, `require_exact_official_targets` y helpers relacionados no amplían el scope público.
- Revisar cualquier punto de entrada CLI o utilitario que pueda reconstruir listas divergentes en vez de consumir la política canónica.
- Verificar que la ayuda por tiers y los mensajes al usuario usan exclusivamente nombres canónicos.

**Notas de implementación**

- Este ticket se rige por `docs/targets_policy.md` para nombres canónicos y por la separación pública entre targets oficiales y aliases legacy solo internos.
- No cambiar el set de 8 targets: solo blindar la fuente de verdad y sus consumidores.

### Ticket A2 — Blindar el registro de backends oficiales

| Campo | Detalle |
|---|---|
| Estado | Pendiente |
| Responsable sugerido | Equipo transpilers |
| Dependencias | A1 recomendado antes de cerrar |
| Archivos a revisar | `src/pcobra/cobra/transpilers/registry.py` |
| Archivos relacionados | `src/pcobra/cobra/transpilers/targets.py`, `src/pcobra/cobra/cli/commands/compile_cmd.py`, árbol `src/pcobra/cobra/transpilers/transpiler/to_*.py` |
| Validaciones reales | `python scripts/ci/validate_targets.py`; `python -m pytest tests/unit/test_official_targets_consistency.py` |
| Criterio de cierre verificable | `TRANSPILER_CLASS_PATHS` coincide exactamente con `OFFICIAL_TARGETS`, en orden oficial, y el árbol productivo no contiene `to_*.py` no oficiales activos. |

**Trabajo esperado**

- Auditar `TRANSPILER_CLASS_PATHS` y cualquier carga dinámica relacionada.
- Verificar que la CLI de compilación no mantiene tablas paralelas fuera del registro canónico.
- Asegurar que si aparece un backend nuevo o legacy, falle la validación CI antes de integrarse.

**Notas de implementación**

- Este ticket conecta directamente con la regla de mantenimiento de `docs/targets_policy.md` y con la auditoría anti-regresión de `scripts/ci/validate_targets.py`.
- Si existe material experimental, debe salir del registro oficial y quedar fuera del árbol productivo/registrado.

---

### Ticket B1 — Auditoría de documentación pública

| Campo | Detalle |
|---|---|
| Estado | Pendiente |
| Responsable sugerido | Equipo docs + CLI |
| Dependencias | A1 y A2 deseables para fijar nombres/registro canónicos |
| Archivos a revisar | `README.md`, `docs/lenguajes.rst`, `docs/lenguajes_soportados.rst`, `docs/targets_policy.md` |
| Archivos normativos a vincular | `docs/matriz_transpiladores.md`, `docs/contrato_runtime_holobit.md` |
| Validaciones reales | `python -m pytest tests/unit/test_public_docs_scope.py`; `python scripts/validate_targets_policy.py` |
| Criterio de cierre verificable | La documentación principal solo enumera como destinos oficiales los 8 targets ya recortados, distingue transpilación vs runtime y no promociona targets retirados, aliases legacy ni compatibilidad Holobit inflada. |

**Trabajo esperado**

- Revisar listas, tablas, snippets CLI y texto narrativo para detectar menciones obsoletas.
- Asegurar que experimentos o históricos sigan segregados en `docs/experimental/` o `docs/historico/` con etiquetas visibles.
- Insertar referencias explícitas a `docs/targets_policy.md`, `docs/matriz_transpiladores.md` y `docs/contrato_runtime_holobit.md` cuando el documento trate alcance, runtime o contrato Holobit.

**Notas de implementación**

- Este ticket no debe reinterpretar la política: debe remitir a los documentos normativos ya vigentes.
- Cualquier ejemplo público debe usar nombres canónicos y evitar aliases legacy del backend JavaScript o nombres narrativos no canónicos del backend `asm` cuando se presenten opciones de CLI.

### Ticket B2 — Auditoría de tests y tooling que declaran backends

| Campo | Detalle |
|---|---|
| Estado | Pendiente |
| Responsable sugerido | Equipo CI/tests |
| Dependencias | A1 y A2 |
| Archivos a revisar | `scripts/validate_targets_policy.py`, `scripts/ci/validate_targets.py`, `tests/utils/targets.py`, `scripts/benchmarks/targets_policy.py` |
| Tests a revisar | `tests/unit/test_official_targets_consistency.py`, `tests/unit/test_validate_targets_policy_script.py`, `tests/unit/test_target_execution_policy.py` |
| Validaciones reales | `python -m pytest tests/unit/test_official_targets_consistency.py`; `python -m pytest tests/unit/test_validate_targets_policy_script.py`; `python scripts/validate_targets_policy.py`; `python scripts/ci/validate_targets.py` |
| Criterio de cierre verificable | No quedan listas públicas o auxiliares divergentes respecto a `OFFICIAL_TARGETS`, `OFFICIAL_RUNTIME_TARGETS`, `TRANSPILATION_ONLY_TARGETS` y la política reverse vigente. |

**Trabajo esperado**

- Sustituir listas hardcodeadas por importaciones desde la política oficial cuando el contexto lo permita.
- Revisar benchmarks, helpers y scripts para evitar reintroducir aliases o targets fuera de política.
- Garantizar que las validaciones detectan condicionales, tablas o módulos retirados antes de llegar a CI verde.

**Notas de implementación**

- Este ticket es la red de seguridad para que la limpieza no dependa solo de revisión manual.
- Debe mantenerse alineado con `docs/targets_policy.md` en el apartado de “Cobertura exacta de la validación automática”.

---

### Ticket C1 — Mantener la matriz contractual Holobit por backend

| Campo | Detalle |
|---|---|
| Estado | Pendiente |
| Responsable sugerido | Equipo transpilers + runtime |
| Dependencias | A1/A2 para set oficial estable |
| Archivos a revisar | `src/pcobra/cobra/transpilers/compatibility_matrix.py` |
| Archivos normativos a vincular | `docs/matriz_transpiladores.md`, `docs/contrato_runtime_holobit.md`, `docs/targets_policy.md` |
| Validaciones reales | `python -m pytest tests/unit/test_holobit_backend_contract_matrix.py`; `python -m pytest tests/integration/transpilers/test_official_backends_contracts.py` |
| Criterio de cierre verificable | La matriz de código y las tablas de documentación dicen exactamente lo mismo: `python` permanece `full`; `javascript`, `rust`, `wasm`, `go`, `cpp`, `java` y `asm` permanecen `partial` mientras no exista paridad real. |

**Trabajo esperado**

- Confirmar que `BACKEND_COMPATIBILITY`, `MIN_REQUIRED_BACKEND_COMPATIBILITY`, notas de evidencia y tiers siguen alineados con la documentación contractual.
- Verificar que ningún documento público promociona soporte Holobit total fuera de Python.
- Revisar si el wording de evidencia técnica sigue correspondiendo con el codegen y los errores esperados en tests.

**Notas de implementación**

- Este ticket debe leerse siempre junto con `docs/matriz_transpiladores.md` y `docs/contrato_runtime_holobit.md` para no duplicar ni reinterpretar el contrato.
- El objetivo no es subir niveles artificialmente, sino evitar regresiones y sobrepromesas.

### Ticket C2 — Garantizar hooks/imports mínimos de `corelibs` y `standard_library`

| Campo | Detalle |
|---|---|
| Estado | Pendiente |
| Responsable sugerido | Equipo transpilers |
| Dependencias | C1 |
| Archivos a revisar | `src/pcobra/cobra/transpilers/compatibility_matrix.py`, backends `src/pcobra/cobra/transpilers/transpiler/to_*.py` implicados |
| Tests a revisar | `tests/unit/test_holobit_backend_contract_matrix.py`, `tests/integration/transpilers/test_official_backends_tier1.py`, `tests/integration/transpilers/test_official_backends_tier2.py`, `tests/integration/transpilers/test_official_backends_contracts.py` |
| Validaciones reales | `python -m pytest tests/integration/transpilers/test_official_backends_tier1.py`; `python -m pytest tests/integration/transpilers/test_official_backends_tier2.py`; `python -m pytest tests/integration/transpilers/test_official_backends_contracts.py` |
| Criterio de cierre verificable | Cada backend oficial genera imports/includes/hooks mínimos esperados; si la feature no existe en runtime real, falla de forma explícita y documentada, nunca con no-op silencioso. |

**Trabajo esperado**

- Revisar generación de hooks `cobra_*` e imports mínimos por backend.
- Verificar que `proyectar`, `transformar` y `graficar` no se degradan silenciosamente en backends `partial`.
- Mantener alineados snapshots/golden files, expectativas de imports y mensajes de error contractual.

**Notas de implementación**

- La pauta normativa de error explícito está en `docs/contrato_runtime_holobit.md`.
- La lectura del nivel `partial` debe venir de `docs/matriz_transpiladores.md`, no de interpretación libre del implementador.

---

### Ticket D1 — Mantener separación entre generación y ejecución

| Campo | Detalle |
|---|---|
| Estado | Pendiente |
| Responsable sugerido | Equipo CLI/runtime |
| Dependencias | A1 y B2 |
| Archivos a revisar | `src/pcobra/cobra/cli/target_policies.py`, `src/pcobra/core/sandbox.py` |
| Archivos relacionados | `docs/targets_policy.md`, `docs/matriz_transpiladores.md`, `docs/contrato_runtime_holobit.md` |
| Validaciones reales | `python -m pytest tests/unit/test_official_targets_consistency.py`; `python -m pytest tests/unit/test_target_execution_policy.py`; `python scripts/validate_targets_policy.py` |
| Criterio de cierre verificable | La política pública y la implementación distinguen con claridad targets oficiales de transpilación, runtime oficial, runtime best-effort y targets solo de generación; no se vende equivalencia de ejecución para los 8 backends. |

**Trabajo esperado**

- Revisar las listas `OFFICIAL_TRANSPILATION_TARGETS`, `OFFICIAL_RUNTIME_TARGETS`, `TRANSPILATION_ONLY_TARGETS` y `VERIFICATION_EXECUTABLE_TARGETS`.
- Confirmar que sandbox, CLI y documentación no presentan `wasm`, `asm`, `go` o `java` como si tuvieran el mismo runtime oficial que `python`, `rust`, `javascript` y `cpp`.
- Alinear wording técnico con la separación ya definida en `docs/targets_policy.md`.

**Notas de implementación**

- Este ticket no reduce ni amplía destinos de transpilación; solo aclara y blinda la separación con runtime.
- Las referencias documentales deben apuntar a la política oficial para evitar listas paralelas.

### Ticket D2 — Ajustar mensajes de usuario y ayudas CLI

| Campo | Detalle |
|---|---|
| Estado | Pendiente |
| Responsable sugerido | Equipo CLI |
| Dependencias | D1 |
| Archivos a revisar | `src/pcobra/cobra/cli/target_policies.py`, comandos CLI que consumen estos mensajes |
| Tests a revisar | `tests/unit/test_cli_target_aliases.py`, `tests/unit/test_official_targets_consistency.py` |
| Validaciones reales | `python -m pytest tests/unit/test_cli_target_aliases.py`; `python -m pytest tests/unit/test_official_targets_consistency.py` |
| Criterio de cierre verificable | Los errores, ayudas y mensajes distinguen “target oficial de salida” de “target con runtime oficial”, y la UX no reintroduce aliases legacy del backend JavaScript ni etiquetas ambiguas como si fueran nombres CLI válidos. |

**Trabajo esperado**

- Revisar textos de error para targets restringidos por capacidad.
- Comprobar que `build_target_help_by_tier` y mensajes derivados no inducen a pensar que todos los targets ejecutan igual.
- Mantener la experiencia de usuario coherente con la política canónica sin reabrir compatibilidad legacy.

**Notas de implementación**

- Este ticket depende de que D1 deje clara la taxonomía runtime/transpilación.
- La prueba relevante aquí no es solo funcional; también es semántica/documental en la UX.

---

### Ticket E1 — Revisar el árbol de backends y reverse activos

| Campo | Detalle |
|---|---|
| Estado | Pendiente |
| Responsable sugerido | Equipo transpilers + CI |
| Dependencias | A2 y B2 |
| Archivos/rutas a revisar | árbol `src/pcobra/cobra/transpilers/transpiler/`, árbol `src/pcobra/cobra/transpilers/reverse/`, `scripts/ci/validate_targets.py` |
| Tests a revisar | `tests/unit/test_official_targets_consistency.py`, `tests/unit/test_reverse_scope_docs_consistency.py` |
| Validaciones reales | `python scripts/ci/validate_targets.py`; `python -m pytest tests/unit/test_official_targets_consistency.py`; `python -m pytest tests/unit/test_reverse_scope_docs_consistency.py` |
| Criterio de cierre verificable | No aparecen nuevos `to_*.py` ni `from_*.py` fuera de política en rutas productivas; cualquier experimento nuevo queda segregado y fuera del registro oficial. |

**Trabajo esperado**

- Auditar el árbol para detectar restos activos o nuevos módulos fuera del alcance oficial.
- Asegurar que el alcance reverse se mantiene como política separada y no reabre targets de salida retirados.
- Revisar imports, módulos huérfanos y referencias documentales a implementaciones reverse ya retiradas.

**Notas de implementación**

- La validación debe apoyarse en `scripts/ci/validate_targets.py`, no en inspección manual ad hoc.
- Si un experimento necesita conservarse, debe vivir fuera de rutas productivas y fuera del registro canónico.

### Ticket E2 — Congelar alcance y criterios de mantenimiento

| Campo | Detalle |
|---|---|
| Estado | Pendiente |
| Responsable sugerido | Equipo maintainers |
| Dependencias | A–E1 cerrados o estabilizados |
| Archivos a revisar | `docs/proposals/recorte_targets_oficiales_tareas.md`, `docs/targets_policy.md`, scripts/tests de validación |
| Validaciones reales | `python scripts/validate_targets_policy.py`; `python scripts/ci/validate_targets.py` |
| Criterio de cierre verificable | El alcance oficial puede auditarse sin interpretación manual adicional: documento madre, política, matriz, contrato Holobit, scripts y tests apuntan al mismo contrato mínimo. |

**Trabajo esperado**

- Mantener este documento como checklist viva del cierre operativo.
- Exigir que cualquier ampliación futura de alcance venga acompañada por cambios coordinados en código, documentación, scripts y tests.
- Registrar dependencias y criterios de cierre de forma que una persona nueva en el repo pueda ejecutar la batería y confirmar el estado real.

**Notas de implementación**

- Este ticket consolida gobernanza, no funcionalidad nueva.
- Si cambia la política oficial en el futuro, este archivo debe actualizarse junto con `docs/targets_policy.md` y las validaciones automáticas.

---

## Dependencias entre tickets

Orden recomendado y dependencias explícitas:

1. **A1** → fijar fuente de verdad y helpers.
2. **A2** → cerrar registro y árbol oficial de backends.
3. **B1** + **B2** → limpiar documentación pública, tests y tooling que puedan divergir.
4. **C1** → alinear la matriz contractual con la documentación normativa.
5. **C2** → blindar hooks/imports mínimos y errores explícitos por backend.
6. **D1** → reforzar separación transpilación/runtime en implementación y documentación.
7. **D2** → ajustar UX y mensajes CLI conforme a esa separación.
8. **E1** → barrer restos en árbol productivo y reverse activo.
9. **E2** → congelar el cierre operativo y el criterio de mantenimiento.

## Definición práctica de “cerrado”

Un ticket de esta propuesta solo debe marcarse como **cerrado** cuando se cumplan simultáneamente estos puntos:

1. el diff toca los archivos concretos asociados al ticket o confirma explícitamente que no requieren cambios;
2. los documentos normativos vinculados (`docs/targets_policy.md`, `docs/matriz_transpiladores.md`, `docs/contrato_runtime_holobit.md`) siguen alineados;
3. las validaciones reales indicadas en el ticket se ejecutan y quedan en verde;
4. no se altera el set oficial de 8 targets, salvo una decisión de producto separada y documentada fuera de esta propuesta.

## Resultado esperado

Al cerrar esta batería:

- pCobra mantiene formalmente el alcance ya recortado a **8 targets oficiales de salida**;
- desaparecen restos productivos/documentales que puedan reabrir targets legacy o aliases públicos;
- la CI blinda la reintroducción de divergencias entre código, CLI, tests y documentación;
- el contrato Holobit/`corelibs`/`standard_library` queda mantenido sin sobredimensionar compatibilidad real ni runtime oficial.
