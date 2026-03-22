# Documentación experimental

Esta carpeta queda reservada para material experimental **vigente** que no forme
parte de la política oficial de targets de salida de Cobra.

## Estado y alcance

- **experimental**: prototipos, pipelines auxiliares o capacidades internas sin
  soporte contractual oficial;
- **de investigación**: material técnico conservado para discusión o diseño
  futuro.

## Regla de separación

La documentación principal del proyecto solo puede presentar como **targets
oficiales de salida** los 8 destinos canónicos definidos en
`src/pcobra/cobra/transpilers/targets.py`.

Los artefactos históricos retirados del producto actual ya no deben residir en
esta carpeta: se conservan fuera del árbol principal distribuido, en
`archive/retired_targets/`.
