# Tareas estructuradas para consolidar el recorte de targets oficiales

## Objetivo

Consolidar pCobra para que el alcance oficial de transpilación quede limitado a estos lenguajes y tiers:

### Tier 1
- `python`
- `rust`
- `javascript`
- `wasm`

### Tier 2
- `go`
- `cpp`
- `java`
- `asm`

Este plan separa las tareas en bloques pequeños, verificables y compatibles con el contrato actual de Holobit SDK, `corelibs` y `standard_library`.

---

## Bloque A — Cerrar la fuente de verdad de targets

### A1. Verificar constantes canónicas
- Revisar `src/pcobra/cobra/transpilers/targets.py`.
- Confirmar que `TIER1_TARGETS`, `TIER2_TARGETS` y `OFFICIAL_TARGETS` contienen exclusivamente los 8 targets oficiales.
- Rechazar cualquier alias legacy en helpers públicos.

**Criterio de cierre**
- La CLI, la GUI y el registro usan únicamente targets canónicos.

**Validación**
- `python -m pytest tests/unit/test_official_targets_consistency.py`

### A2. Blindar el registro de backends
- Revisar `src/pcobra/cobra/transpilers/registry.py`.
- Confirmar que solo existen clases registradas para los 8 targets oficiales.
- Bloquear la reintroducción de módulos `to_*.py` no oficiales.

**Criterio de cierre**
- El registro coincide exactamente con `OFFICIAL_TARGETS`.

**Validación**
- `python scripts/ci/validate_targets.py`

---

## Bloque B — Eliminar restos públicos de otros lenguajes

### B1. Auditoría de documentación pública
- Revisar `README.md`, `docs/lenguajes.rst`, `docs/lenguajes_soportados.rst` y `docs/targets_policy.md`.
- Eliminar referencias públicas a targets retirados, aliases legacy o snippets ambiguos.
- Mantener fuera del alcance público cualquier material experimental en `docs/experimental/` o `docs/historico/`.

**Criterio de cierre**
- La documentación principal solo enumera `python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java` y `asm` como destinos oficiales.

**Validación**
- `python -m pytest tests/unit/test_public_docs_scope.py`
- `python scripts/validate_targets_policy.py`

### B2. Auditoría de tests y tooling
- Revisar suites, scripts y utilidades que declaren listas de backends.
- Sustituir listas hardcodeadas por importaciones desde la política oficial cuando sea posible.
- Asegurar que benchmarks y validadores no reintroducen backends fuera del scope.

**Criterio de cierre**
- No hay listas públicas divergentes respecto a `OFFICIAL_TARGETS`.

**Validación**
- `python -m pytest tests/unit/test_official_targets_consistency.py`

---

## Bloque C — Compatibilidad con Holobit SDK y librerías base

### C1. Mantener contrato Holobit por backend
- Revisar `src/pcobra/cobra/transpilers/compatibility_matrix.py`.
- Conservar `python` como backend `full`.
- Mantener `javascript`, `rust`, `wasm`, `go`, `cpp`, `java` y `asm` como `partial` mientras su runtime no alcance paridad real.
- No documentar compatibilidad total con `holobit-sdk` fuera de Python.

**Criterio de cierre**
- La documentación y la matriz contractual dicen lo mismo.

**Validación**
- `python -m pytest tests/unit/test_holobit_backend_contract_matrix.py`
- `python -m pytest tests/integration/transpilers/test_official_backends_contracts.py`

### C2. Garantizar imports/hook mínimos de `corelibs` y `standard_library`
- Validar que cada backend oficial genera los imports/hook mínimos esperados.
- Si una feature no existe en runtime real, debe fallar de forma explícita y documentada.
- Evitar no-op silencioso en `proyectar`, `transformar` y `graficar`.

**Criterio de cierre**
- Todos los backends oficiales generan código contractual verificable.

**Validación**
- `python -m pytest tests/integration/transpilers/test_official_backends_tier1.py`
- `python -m pytest tests/integration/transpilers/test_official_backends_tier2.py`

---

## Bloque D — Separar transpilación de runtime

### D1. Mantener separación entre generación y ejecución
- Revisar `src/pcobra/cobra/cli/target_policies.py` y `src/pcobra/core/sandbox.py`.
- Confirmar que los 8 targets son oficiales para transpilación.
- Confirmar que el runtime oficial sigue limitado al subconjunto documentado.

**Criterio de cierre**
- No se presenta `go`, `java`, `wasm` ni `asm` como runtime Docker/sandbox equivalente.

**Validación**
- `python -m pytest tests/unit/test_official_targets_consistency.py`

### D2. Ajustar mensajes de usuario
- Hacer que errores y ayudas distingan claramente entre “target oficial de salida” y “target con runtime oficial”.
- Mantener la UX canónica sin aliases como `js` o `ensamblador`.

**Criterio de cierre**
- La CLI no induce a pensar que todos los targets compilan y ejecutan igual.

**Validación**
- `python -m pytest tests/unit/test_cli_target_aliases.py`

---

## Bloque E — Cierre operativo

### E1. Revisar árbol de backends
- Confirmar que el repositorio no contiene nuevos `to_*.py` ni `from_*.py` fuera de política.
- Si aparece un experimento nuevo, moverlo a una zona experimental o fuera del registro oficial.

**Criterio de cierre**
- No quedan restos activos de targets no oficiales en rutas productivas.

**Validación**
- `python scripts/ci/validate_targets.py`

### E2. Congelar el alcance en documentación de mantenimiento
- Actualizar el plan por tiers y este archivo cuando cambie el alcance oficial.
- Exigir que cualquier ampliación futura incluya código, tests, documentación y validaciones CI.

**Criterio de cierre**
- El alcance oficial puede auditarse sin interpretación manual adicional.

**Validación**
- `python scripts/validate_targets_policy.py`

---

## Orden recomendado de ejecución

1. **Bloque A**: fuente de verdad y registro.
2. **Bloque B**: limpieza pública y tooling.
3. **Bloque C**: Holobit SDK, `corelibs` y `standard_library`.
4. **Bloque D**: separación runtime/transpilación.
5. **Bloque E**: cierre operativo y congelación del alcance.

## Resultado esperado

Al cerrar estas tareas, pCobra queda formalmente acotado a 8 targets oficiales de salida, sin reintroducir otros lenguajes en el árbol productivo y sin sobredimensionar la compatibilidad real con Holobit SDK ni con las librerías base del proyecto.
