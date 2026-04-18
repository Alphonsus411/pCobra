# Índice del ecosistema unificado de Cobra

Este documento define el **índice contractual** para evitar ambigüedad sobre qué módulos son fuente canónica y cuáles existen únicamente por compatibilidad.

## 1) Fuente canónica contractual única

Los siguientes módulos son la única referencia autorizada para política pública de backends y arquitectura unificada:

- `src/pcobra/cobra/architecture/backend_policy.py`
- `src/pcobra/cobra/architecture/contracts.py`
- `src/pcobra/cobra/architecture/unified_ecosystem.py`

> Regla: cualquier módulo fuera de esta lista debe **importar y reutilizar** estas definiciones, sin duplicar listas públicas de backends.

## 2) Módulos contractuales (consumo público)

- `src/pcobra/cobra/architecture/backend_policy.py` (política pública/legacy)
- `src/pcobra/cobra/architecture/contracts.py` (capabilities + fallback público)
- `src/pcobra/cobra/architecture/unified_ecosystem.py` (blueprint y plan unificado)
- `src/pcobra/cobra/build/backend_pipeline.py` (entrypoint de resolución para rutas de usuario)
- `src/pcobra/cobra/bindings/*` (integración runtime/bindings)

## 3) Módulos de compatibilidad (internal compatibility only)

Estos módulos no forman parte de una API pública estable y se mantienen para backward compatibility:

- `src/cobra/cli/__init__.py`
- `src/cobra/cli/cli.py`
- `src/cobra/cli/target_policies.py`
- `src/cobra/transpilers/__init__.py`
- `src/cobra/transpilers/targets.py`
- `src/cobra/transpilers/registry.py`
- `src/cobra/transpilers/compatibility_matrix.py`

## 4) Guardrail CI asociado

La validación `scripts/ci/validate_public_backend_literals.py` falla si detecta listas literales de backends públicos fuera de:

- `src/pcobra/cobra/architecture/*`
- `src/pcobra/cobra/build/backend_pipeline.py`
- `src/pcobra/cobra/bindings/*`

De esta forma se garantiza que la evolución del contrato público tenga una fuente de verdad única.
