# Mantenimiento histórico de aliases/targets retirados

Estas auditorías **no forman parte del pipeline canónico principal**.

Se mantienen para tareas puntuales de migración en repos externos o revisiones históricas:

- `python scripts/audit_retired_targets.py <ruta>`
- `python scripts/lint_legacy_aliases.py`
- Modo estricto opcional: `python scripts/lint_legacy_aliases.py --fail-on-findings`

El pipeline principal debe centrarse en validaciones del set canónico:
`python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java`, `asm`.
