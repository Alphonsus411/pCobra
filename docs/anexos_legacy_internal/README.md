# Anexos legacy/internal

> ⚠️ **NO PÚBLICO / NO ONBOARDING**: este directorio concentra material histórico y de compatibilidad interna.
> No debe usarse como documentación principal para usuarios nuevos.

Este directorio agrupa documentación histórica y notas internas para mantener limpio el onboarding del README principal.

## Contenido

- Migración de CLI unificada (aliases y comandos legacy):
  - [`docs/migracion_cli_unificada.md`](../migracion_cli_unificada.md)
- Migración de targets retirados de la UX pública:
  - [`docs/migracion_targets_retirados.md`](../migracion_targets_retirados.md)
- Histórico general del proyecto:
  - [`docs/historico/`](../historico/)

## Uso recomendado

Si eres usuario nuevo, empieza por `README.md` y usa solo la CLI pública:

- `cobra run`
- `cobra build`
- `cobra test`
- `cobra mod`

Consulta estos anexos únicamente cuando necesites migrar scripts antiguos o diagnosticar compatibilidad histórica.
