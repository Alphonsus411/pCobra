# Contrato oficial de resolución de imports (`CobraImportResolver`)

Este documento define el contrato **oficial** y estable del resolvedor de imports de Cobra para eliminar ambigüedades operativas entre stdlib, módulos de proyecto, bridge Python e híbridos.

## 1) Orden oficial de resolución (`_SOURCE_ORDER`)

El orden vigente de precedencia es:

1. `stdlib`
2. `project`
3. `python_bridge`
4. `hybrid`

En términos prácticos:

- Si `importar datos` coincide con `cobra.datos` y también existe un módulo local `datos`, se resuelve primero como stdlib (`cobra.datos`).
- Cuando un nombre sin namespace coincide en múltiples orígenes, el resultado efectivo siempre sigue el orden anterior.

## 2) Política explícita para imports ambiguos

Se considera ambiguo un import sin namespace (sin `.`) que tenga más de un candidato válido entre los orígenes del contrato.

### Modo por defecto (no estricto)

- El resolver emite `UserWarning`.
- Se selecciona automáticamente el candidato de mayor prioridad según `_SOURCE_ORDER`.

### Strict mode (`strict_ambiguous_imports=True`)

- El resolver **falla** con `ImportResolutionError`.
- La resolución automática queda deshabilitada para imports ambiguos.
- Se exige import explícito para desambiguar.

## 3) Prefijos recomendados para evitar colisiones

Recomendaciones normativas:

- **Stdlib Cobra**: usar siempre `cobra.*` cuando el módulo pueda colisionar (`cobra.datos`, `cobra.web`, etc.).
- **Módulos de proyecto**: usar namespace de aplicación (por ejemplo `app.datos`, `mi_equipo.datos`) en lugar de nombres planos como `datos`.
- **Bridge Python**: preferir nombres plenamente calificados cuando aplique (`json`, `datetime`, `paquete.submodulo`) y evitar nombres genéricos que colisionen con stdlib/proyecto.

## 4) Metadata de observabilidad en módulos cargados

Cuando el resolvedor carga un módulo Python (`load_module`), inyecta metadata para diagnóstico:

- `__cobra_resolution_source__`: origen efectivo (`stdlib`, `project`, `python_bridge`, `hybrid`).
- `__cobra_backend_injected__`: backend efectivo inyectado.
- `__cobra_resolution_metadata__`: snapshot estructurado con:
  - `request`
  - `source`
  - `resolved_name`
  - `backend`
  - `import_path`

Esta metadata habilita trazabilidad de resolución y debugging en runtime sin inspección adicional del resolvedor.
