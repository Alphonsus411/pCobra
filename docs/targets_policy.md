# Política oficial de targets

> ⚠️ Documento parcialmente derivado: los bloques marcados como `BEGIN/END GENERATED`
> son **obligatorios**, se regeneran automáticamente y no deben editarse manualmente.

Este documento fija la narrativa pública canónica de pCobra: el proyecto **transpila únicamente a 8 backends oficiales** agrupados en **Tier 1** y **Tier 2**. Cualquier otra denominación, alias o artefacto de implementación queda fuera de las páginas públicas activas.

## Fuente única de verdad

La fuente única de verdad para los backends oficiales de salida es `src/pcobra/cobra/config/transpile_targets.py`.

Ese módulo define exactamente:

- `TIER1_TARGETS`
- `TIER2_TARGETS`
- `OFFICIAL_TARGETS`
- `TARGETS_BY_TIER` con grupos explícitos `tier_1`/`tier_2`
- `TARGET_METADATA` con estado, prioridad de release, mantenedor opcional y bandera `holobit_compatible`

La política operativa de runtime, Holobit y SDK se deriva de `src/pcobra/cobra/cli/target_policies.py` y `src/pcobra/cobra/transpilers/compatibility_matrix.py`.

## Lista exacta de backends oficiales

`OFFICIAL_TARGETS` debe ser siempre la concatenación exacta de `TIER1_TARGETS + TIER2_TARGETS`.

<!-- BEGIN GENERATED TARGET TIERS -->
### Tier 1

- `python`
- `rust`
- `javascript`
- `wasm`

### Tier 2

- `go`
- `cpp`
- `java`
- `asm`
<!-- END GENERATED TARGET TIERS -->

En CLI, documentación, ejemplos, tablas y configuración pública **solo** se aceptan esos 8 nombres canónicos.

## Declaraciones explícitas del contrato vigente

Para evitar ambigüedades editoriales y de implementación, esta política fija de forma explícita que:

1. El set oficial de backends de salida es **exactamente 8** y coincide 1:1 con `OFFICIAL_TARGETS`.
2. La compatibilidad SDK **completa** existe únicamente para `python`.
3. El resto de backends oficiales (`rust`, `javascript`, `wasm`, `go`, `cpp`, `java`, `asm`) mantiene únicamente compatibilidad **parcial contractual** según la matriz de compatibilidad.

## Gobernanza de cambios de targets

La lista canónica de 8 targets (`TIER1_TARGETS`, `TIER2_TARGETS`, `OFFICIAL_TARGETS`) está congelada por contrato operativo.

Cualquier extensión del alcance (por ejemplo, introducir un noveno target, mover targets entre tiers, o reemplazar un nombre canónico) **requiere obligatoriamente**:

1. RFC explícita aprobada por mantenedores.
2. Plan de migración versionado (código, CLI, documentación, pruebas y artefactos).
3. Comunicación de compatibilidad/ruptura en changelog y notas de release.

No se permiten ampliaciones silenciosas ni “pequeños” cambios ad hoc al registro/CLI que alteren el conjunto oficial sin ese proceso.

## Política de soporte (Tier 1 vs Tier 2) y SLA

Definición pública:

- **Tier 1**: cobertura prioritaria de regresiones de transpilación y consistencia documental.
- **Tier 2**: soporte contractual mantenido con prioridad secundaria frente a Tier 1.

SLA de triage para incidencias de regresión:

- **Tier 1**: triage inicial en **<= 2 días hábiles**.
- **Tier 2**: triage inicial en **<= 5 días hábiles**.

### Criterios de promoción y degradación

Promoción (**Tier 2 → Tier 1**), solo con señal sostenida en dos releases consecutivas:

1. Uso real consistente.
2. Cobertura/gates de CI mantenidos.
3. Estabilidad contractual (CLI, documentación y comportamiento técnico alineados).

Degradación (**Tier 1 → Tier 2**):

1. Incumplimiento sostenido de calidad o cobertura CI.
2. Bloqueos de dependencias/toolchain incompatibles con la ventana de mantenimiento.
3. Desalineación contractual repetida entre runtime/CLI/documentación.

Toda promoción/degradación requiere RFC, plan de migración y comunicación explícita en changelog/notas de release.

### Regla de bloqueo para el noveno target

Queda explícitamente bloqueado introducir una novena clave de backend en el registro (`TRANSPILER_CLASS_PATHS`) o en validadores CLI sin pasar por RFC + migración.

Cualquier intento de ampliar el set canónico debe fallar de forma ruidosa en tests/unitarios y en validaciones de arranque del módulo, para evitar drift silencioso entre código, CLI y documentación.

## Estado público por backend

<!-- BEGIN GENERATED TARGET STATUS TABLE -->
| Backend | Tier | Runtime público | Estado Holobit público | Compatibilidad SDK real |
|---|---|---|---|---|
| `python` | Tier 1 | oficial verificable | `full`; usa el contrato completo del SDK Python | completa |
| `rust` | Tier 1 | oficial verificable | adaptador mantenido por el proyecto; estado contractual `partial` | parcial |
| `javascript` | Tier 1 | oficial verificable | adaptador mantenido por el proyecto; estado contractual `partial` | parcial |
| `wasm` | Tier 1 | solo transpilación | hooks simbólicos/diagnóstico `partial`; requiere runtime externo | parcial |
| `go` | Tier 2 | best-effort no público | hooks/adaptadores `partial` sobre runtime best-effort | parcial |
| `cpp` | Tier 2 | oficial verificable | adaptador mantenido por el proyecto; estado contractual `partial` | parcial |
| `java` | Tier 2 | best-effort no público | hooks/adaptadores `partial` sobre runtime best-effort | parcial |
| `asm` | Tier 2 | solo transpilación | hooks simbólicos/diagnóstico `partial`; requiere runtime externo | parcial |
<!-- END GENERATED TARGET STATUS TABLE -->

Lectura normativa de la tabla:

- `python` es el único backend que puede presentarse como compatibilidad SDK completa.
- `rust`, `javascript` y `cpp` tienen runtime oficial verificable y adaptador Holobit mantenido, pero **siguen siendo `partial`** a nivel contractual.
- `go` y `java` siguen siendo backends oficiales de salida con runtime best-effort, pero no deben describirse como equivalentes a un runtime oficial público ni a compatibilidad SDK completa.
- `wasm` y `asm` siguen siendo backends oficiales de salida solo de transpilación, pero no deben describirse como equivalentes a un runtime oficial público ni a compatibilidad SDK completa.

## Alcance del contrato

Los 8 nombres de `OFFICIAL_TARGETS` describen el alcance oficial de **transpilación de salida**.

Eso no implica que todos los backends prometan el mismo runtime ni la misma cobertura de librerías. La separación pública correcta es:

<!-- BEGIN GENERATED TARGET RUNTIME SPLIT -->
- `OFFICIAL_RUNTIME_TARGETS`: `python`, `rust`, `javascript`, `cpp`
- `VERIFICATION_EXECUTABLE_TARGETS`: `python`, `rust`, `javascript`, `cpp`
- `BEST_EFFORT_RUNTIME_TARGETS`: `go`, `java`
- `TRANSPILATION_ONLY_TARGETS`: `wasm`, `asm`
- `NO_RUNTIME_TARGETS`: `wasm`, `asm`
- `OFFICIAL_STANDARD_LIBRARY_TARGETS`: `python`, `rust`, `javascript`, `cpp`
- `ADVANCED_HOLOBIT_RUNTIME_TARGETS`: `python`, `rust`, `javascript`, `cpp`
- `SDK_COMPATIBLE_TARGETS`: `python`
<!-- END GENERATED TARGET RUNTIME SPLIT -->

La matriz contractual por backend y feature vive en `src/pcobra/cobra/transpilers/compatibility_matrix.py` y se publica en `docs/matriz_transpiladores.md`.

## Reglas de redacción pública

La documentación pública activa debe respetar estas reglas editoriales:

1. Presentar siempre una sola narrativa: pCobra transpila a **8 backends oficiales**.
2. Nombrar únicamente los identificadores canónicos `python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java` y `asm`.
3. Distinguir explícitamente entre **transpilación oficial**, **runtime oficial verificable**, **runtime best-effort no público** y **solo transpilación**.
4. Describir Holobit solo con el contrato vigente: `python` `full`; el resto, como máximo, `partial` según la matriz contractual.
5. No presentar a ningún backend distinto de `python` como compatibilidad SDK completa.

## Historial de deprecaciones y aliases retirados

La política activa no mantiene ventanas ni aliases legacy en el flujo principal.

Si necesitas contexto histórico (ventanas de deprecación, aliases retirados y cronología de eliminación), consulta el archivo histórico:

- `docs/historico/migracion_targets_retirados_archivo.md`

## Reverse

La transpilación inversa se documenta como capacidad separada. Sus orígenes de entrada se definen en `src/pcobra/cobra/transpilers/reverse/policy.py`.

Esos orígenes reverse **no amplían** `OFFICIAL_TARGETS`: describen entradas aceptadas por `cobra transpilar-inverso`, no targets oficiales de salida. La documentación pública debe hablar de **orígenes reverse** y dejar claro que no son targets de salida.

### Límites de round-trip por target

Contrato técnico actual para validaciones `Cobra -> target -> Cobra`:

- **`python`**: se valida por equivalencia de AST normalizado en fixtures deterministas, removiendo imports estándar del código intermedio antes del reverse (`from core.nativos`, `from corelibs`, `from standard_library`).  
- **`javascript`**: se valida por equivalencia de AST normalizado solo en subconjuntos compatibles con el parser reverse (tree-sitter opcional y sin garantizar soporte para todo el bootstrap/runtime generado).  
- **`java`**: mismo criterio de AST normalizado cuando hay soporte reverse disponible; se considera cobertura parcial y dirigida por fixtures.  
- **`rust`, `go`, `cpp`, `wasm`, `asm`**: hoy no existe parser reverse oficial de entrada para cerrar round-trip automático hacia Cobra; solo aplica transpilación de salida.

Implicación práctica: los reportes de `cobra transpilar-inverso` pueden advertir degradaciones o ausencia de medición automática cuando el target no tiene reverse parser o cuando el parser reverse no soporta nodos concretos.

## Migración para usuarios de targets retirados

La guía oficial de transición para flujos heredados está en `docs/migracion_targets_retirados.md`.
En documentación pública activa deben evitarse snippets de targets retirados; cualquier referencia histórica debe quedar aislada en documentación histórica.
Queda explícito en esta política que **backends retirados no forman parte del árbol operativo** ni del recorrido normativo principal.

## Revisión editorial final

Queda **prohibido reintroducir** en páginas públicas activas:

- alias o nombres alternativos de targets,
- referencias obsoletas mezcladas con la política activa,
- terminología de arquitectura interna presentada como si fuera un backend público,
- comparativas que inflen el soporte Holobit o la compatibilidad SDK.

La única excepción permitida es una sección **claramente separada** de changelog o nota de migración.

## Qué valida automáticamente el repositorio

La política simplificada valida únicamente estos puntos:

1. `TIER1_TARGETS`, `TIER2_TARGETS` y `OFFICIAL_TARGETS` coinciden exactamente.
2. Los registros y artefactos oficiales (`registry.py`, CLI, módulos `to_*.py`, módulos reverse dentro de su scope, golden files y documentación derivada) permanecen alineados con esos 8 backends.
3. La documentación pública y los textos vigilados no reintroducen aliases públicos no canónicos ni estados incompatibles con la matriz contractual.

## Documentación derivada

Los artefactos derivados deben regenerarse desde la política simplificada:

- `docs/_generated/target_policy_summary.md`
- `docs/_generated/target_policy_summary.rst`
- `docs/_generated/official_targets_table.rst`
- `docs/_generated/runtime_capability_matrix.rst`
- `docs/_generated/reverse_scope_table.rst`
- `docs/_generated/cli_backend_examples.rst`
- `docs/matriz_transpiladores.md`

## Comprobaciones recomendadas

```bash
python scripts/generate_target_policy_docs.py
python scripts/generar_matriz_transpiladores.py
python scripts/validate_targets_policy.py
python scripts/ci/validate_targets.py
python -m pytest tests/unit/test_validate_targets_policy_script.py
python -m pytest tests/unit/test_official_targets_consistency.py
```
