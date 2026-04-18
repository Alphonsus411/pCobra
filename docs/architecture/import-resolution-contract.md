# Contrato oficial de resolución de imports (`CobraImportResolver`)

Este documento define el contrato **oficial** y estable del resolvedor de imports de Cobra para eliminar ambigüedades operativas entre stdlib, módulos de proyecto, bridge Python e híbridos.

## 1) Orden oficial de resolución (API contractual)

El orden vigente de precedencia se congela como contrato público en
`RESOLUTION_SOURCE_ORDER`:

1. `stdlib`
2. `project`
3. `python_bridge`
4. `hybrid`

Este orden debe tratarse como **API contractual** y solo puede cambiar en una versión mayor.

En el runtime queda expuesto como:

- `RESOLUTION_SOURCE_ORDER` (tupla contractual vigente)
- `RESOLUTION_SOURCE_ORDER_STABILITY = "major"` (política de estabilidad)

En términos prácticos:

- Si `importar datos` coincide con `cobra.datos` y también existe un módulo local `datos`, se resuelve primero como stdlib (`cobra.datos`).
- Cuando un nombre sin namespace coincide en múltiples orígenes, el resultado efectivo siempre sigue el orden anterior.

## 2) Política explícita para imports ambiguos y códigos de error estables

Se considera ambiguo un import sin namespace (sin `.`) que tenga más de un candidato válido entre los orígenes del contrato.

La política se configura por proyecto en `cobra.toml`:

```toml
[imports]
collision_policy = "warn" # warn | strict_error | namespace_required
```

Si no se declara nada, el resolver usa `namespace_required` (`DEFAULT_COLLISION_POLICY`).

### `warn` (modo de migración/compatibilidad)

- El resolver emite `UserWarning`.
- Se selecciona automáticamente el candidato de mayor prioridad según `RESOLUTION_SOURCE_ORDER`.

### `strict_error`

- El resolver **falla** con `ImportResolutionError`.
- La resolución automática queda deshabilitada para imports ambiguos.
- Se exige import explícito para desambiguar.

### `namespace_required`

- El resolver **falla** con `ImportResolutionError` ante colisiones sin namespace.
- El mensaje exige usar namespace explícito (`cobra.*`, `app.*`, etc.).
- Mantiene el mismo orden de precedencia como contrato estable, pero no permite aplicarlo de forma implícita en imports ambiguos.

> Compatibilidad: `strict_ambiguous_imports=True` sigue soportado y fuerza `strict_error`.

### Códigos de error estables (`ImportResolutionError`)

El resolver adjunta un código máquina estable en `ImportResolutionError.code`
(y en el texto como prefijo `[CODIGO]`) para tooling/CI:

- `IMP-COLLISION-001`: colisión de import sin namespace en `strict_error`/`namespace_required`.
- `IMP-NOT-FOUND-001`: no existe candidato de resolución para el módulo solicitado.
- `IMP-REQUEST-001`: request vacío.
- `IMP-CONFIG-001`: `collision_policy` inválida en configuración.



## 3) Prefijos recomendados para evitar colisiones

Recomendaciones normativas:

- **Stdlib Cobra**: usar siempre `cobra.*` cuando el módulo pueda colisionar (`cobra.datos`, `cobra.web`, etc.).
- **Módulos de proyecto**: usar namespace de aplicación (por ejemplo `app.datos`, `mi_equipo.datos`) en lugar de nombres planos como `datos`.
- **Bridge Python**: preferir nombres plenamente calificados cuando aplique (`json`, `datetime`, `paquete.submodulo`) y evitar nombres genéricos que colisionen con stdlib/proyecto.

## 4) Metadata de observabilidad en módulos cargados y auditoría opcional

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
  - `audit_debug` (si la auditoría de debug está activa)

Adicionalmente, se puede habilitar auditoría opcional:

```toml
[imports]
audit_debug = true
```

Con `audit_debug=true`, cada resolución agrega un evento en `resolver.audit_events` y escribe log `DEBUG` con `request`, `source`, `resolved_name` y `precedence_reason`.

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

Estos 3 casos (`importar pandas`, `importar datos`/`importar cobra.datos`, e híbridos
en `imports.hybrid_modules`) son rutas oficiales del contrato de resolución.

## 6) Patrón recomendado de namespaces y migración de conflictos reales

Patrón normativo recomendado:

- **stdlib Cobra**: `cobra.*`
- **módulos de app/proyecto**: `app.*` (o un namespace organizacional equivalente)

Migraciones sugeridas (casos reales frecuentes):

1. Conflicto `datos` (stdlib vs módulo local):
   - Antes: `importar datos`
   - Después (stdlib): `importar cobra.datos`
   - Después (app): `importar app.datos`

2. Conflicto `web` (stdlib `cobra.web` vs carpeta local `web/`):
   - Antes: `importar web`
   - Después (stdlib): `importar cobra.web`
   - Después (app): `importar app.web`

3. Conflicto con bridge Python (`json`):
   - Si el proyecto crea `app/json.co`, evitar `importar json` en código nuevo.
   - Preferir:
     - bridge Python: `importar json` solo cuando no exista colisión local/stdlib
     - app explícita: `importar app.json`

Esta convención minimiza deuda de migración y evita depender de precedencia implícita en conflictos.
