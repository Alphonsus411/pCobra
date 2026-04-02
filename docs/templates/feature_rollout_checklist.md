# Checklist de rollout de feature de lenguaje

Usa esta plantilla para cualquier feature nueva (`<feature_id>`).

## Identificador

- Feature ID: `<feature_id>`
- PR/RFC: `<enlace>`

## Cobertura técnica

- [ ] gramática/parser/AST
  - Archivos tocados:
- [ ] intérprete
  - Archivos tocados:
- [ ] transpilers oficiales
  - Targets cubiertos: `python`, `javascript`, `rust`, `go`, `cpp`, `java`, `wasm`, `asm`
- [ ] compat matrices
  - Matrices/documentos actualizados:
- [ ] tests unit/integration
  - Tests añadidos/actualizados:
- [ ] docs y ejemplos
  - Documentación:
  - Ejemplo mínimo en `examples/features/<feature_id>/minimal.co`:

## Verificación rápida

```bash
python scripts/ci/audit_feature_rollout.py --feature-id <feature_id>
```
