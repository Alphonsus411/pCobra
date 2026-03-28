# Migración de `archive/retired_targets/`

Fecha: 2026-03-28.

El contenido histórico de `archive/retired_targets/` se separó del repositorio principal para mantener el árbol operativo y la documentación pública enfocados exclusivamente en los 8 backends oficiales vigentes.

A partir de esta migración:

- El repositorio principal ya no incluye `archive/retired_targets/`.
- Las validaciones CI y reglas de empaquetado dejaron de depender del escaneo de ese árbol eliminado.
- Cualquier referencia histórica debe mantenerse en documentos de historial bajo `docs/historico/`.
