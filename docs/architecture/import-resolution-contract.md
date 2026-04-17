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

La política se configura por proyecto en `cobra.toml`:

```toml
[imports]
collision_policy = "warn" # warn | strict_error | namespace_required
```

Si no se declara nada, el resolver usa `warn` por compatibilidad.

### `warn` (modo por defecto)

- El resolver emite `UserWarning`.
- Se selecciona automáticamente el candidato de mayor prioridad según `_SOURCE_ORDER`.

### `strict_error`

- El resolver **falla** con `ImportResolutionError`.
- La resolución automática queda deshabilitada para imports ambiguos.
- Se exige import explícito para desambiguar.

### `namespace_required`

- El resolver **falla** con `ImportResolutionError` ante colisiones sin namespace.
- El mensaje exige usar namespace explícito (`cobra.*`, `app.*`, etc.).
- Mantiene el mismo orden de precedencia como contrato estable, pero no permite aplicarlo de forma implícita en imports ambiguos.

> Compatibilidad: `strict_ambiguous_imports=True` sigue soportado y fuerza `strict_error`.

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
  - `precedence_reason` (motivo de precedencia: selección única o aplicación de orden estable)

Esta metadata habilita trazabilidad de resolución y debugging en runtime sin inspección adicional del resolvedor.

## 5) Casos de referencia (debug operativo)

### Caso A — `importar pandas` (`python_bridge`)

- Si no existe `cobra.pandas` ni módulo de proyecto `pandas`, el candidato único es `python_bridge`.
- Resultado esperado:
  - `source = "python_bridge"`
  - `resolved_name = "pandas"`
  - `precedence_reason = "unique_source:python_bridge"`

### Caso B — `importar datos` (stdlib Cobra)

- Si existe `cobra.datos`, se resuelve a stdlib.
- Si además hay `datos` de proyecto o bridge Python, hay colisión y:
  - con `warn`: se selecciona `cobra.datos` + warning,
  - con `strict_error` o `namespace_required`: falla hasta que el import sea explícito.
- En resolución implícita por colisión:
  - `precedence_reason = "source_order:stdlib > project > python_bridge > hybrid"`

### Caso C — módulo híbrido declarado en config

Declaración en `cobra.toml`:

```toml
[imports.hybrid_modules.mi_hibrido]
import_path = "mi_hibrido_runtime"
backend = "javascript"
```

- `importar mi_hibrido` produce:
  - `source = "hybrid"`
  - `import_path = "mi_hibrido_runtime"`
  - `backend = "javascript"` (si no hay override de contrato por módulo)
  - `precedence_reason = "unique_source:hybrid"`

## 6) Ejemplos de conflictos y resolución explícita

- Conflicto `datos` entre stdlib y proyecto:
  - Implícito: `importar datos` (ambigüedad)
  - Explícito recomendado:
    - stdlib: `importar cobra.datos`
    - proyecto: `importar app.datos`
- Conflicto con bridge Python:
  - Si existe paquete Python `datos`, usar nombre explícito de proyecto o stdlib para evitar depender de orden de precedencia.
