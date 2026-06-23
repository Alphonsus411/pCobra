# Checklist de rollout de feature de lenguaje

Usa esta plantilla para cualquier feature nueva (`<feature_id>`).

## Identificador

- Feature ID: `<feature_id>`
- PR/RFC: `<enlace>`

## Resumen de archivos modificados

- `<ruta>`: `<motivo del cambio>`

## Resumen de pruebas añadidas

- `<ruta_test>`: `<caso cubierto>`
- Si no se añadieron pruebas, justificar por qué no aplica:

## Resultado de comandos ejecutados

- `<comando>`: `<resultado>`
- Indicar cualquier comando que no pudo ejecutarse y el motivo:

## POCs que deben repetirse manualmente

- `<POC/manual>`: `<pasos esperados>`
- Si no hay POCs manuales pendientes, indicar: `No aplica`.

## Confirmaciones explícitas de alcance

- [ ] No se tocó Lexer.
- [ ] No se tocó Parser.
- [ ] No se tocó gramática.
- [ ] No se tocaron tokens.
- [ ] No se tocaron nodos AST.
- [ ] No se tocaron transpiladores.
- [ ] No se cambió sintaxis Cobra.
- [ ] No se añadieron dependencias.

## Cobertura técnica

- [ ] gramática/parser/AST
  - Archivos tocados:
- [ ] intérprete
  - Archivos tocados:
- [ ] transpilers oficiales
  - Targets cubiertos: `python`, `javascript`, `rust`
- [ ] compat matrices
  - Matrices/documentos actualizados:
- [ ] tests unit/integration
  - Tests añadidos/actualizados:
- [ ] docs y ejemplos
  - Documentación:
  - Ejemplo mínimo en `examples/features/<feature_id>/minimal.co`:

## Validaciones manuales no ejecutadas

- `<validación>`: `<motivo>`
- Si todas las validaciones manuales aplicables se ejecutaron, indicar: `No aplica`.

## Verificación rápida

```bash
python scripts/ci/audit_feature_rollout.py --feature-id <feature_id>
```
