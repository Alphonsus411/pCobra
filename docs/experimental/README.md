# Documentación experimental

Esta carpeta reúne documentación pública que **no forma parte de la política oficial de targets de salida** de Cobra.

## Estado y alcance

Todo lo que aparezca bajo `docs/experimental/` debe leerse como una de estas categorías:

- **experimental**: prototipos, pipelines auxiliares o capacidades internas sin soporte contractual oficial;
- **retirado**: pruebas o pipelines que existieron en algún momento, pero ya no forman parte del alcance vigente;
- **de investigación**: material técnico conservado para discusión o diseño futuro.

## Regla de separación

La documentación principal del proyecto solo puede presentar como **targets oficiales de salida** los 8 destinos canónicos definidos en `src/pcobra/cobra/transpilers/targets.py`:

- `python`
- `rust`
- `javascript`
- `wasm`
- `go`
- `cpp`
- `java`
- `asm`

Los contenidos de esta carpeta **no** deben reutilizarse como si fueran soporte oficial en tablas, ejemplos de CLI o claims de compatibilidad pública.

## Índice actual

- `llvm_prototype.md`: experimento de backend LLVM.
- `construcciones_llvm_ir.md`: notas exploratorias de mapeo a LLVM IR.
- `soporte_latex.md`: parser reverse experimental desde pseudocódigo LaTeX.
- `limitaciones_wasm_reverse.md`: referencia retirada del antiguo reverse desde WASM.
- `plan_nuevas_funcionalidades_hololang.md`: bloque archivado de investigación holográfica/Hololang, conservado como material experimental y fuera de política.
