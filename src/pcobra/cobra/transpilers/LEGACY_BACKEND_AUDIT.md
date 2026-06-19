# Auditoría de referencias legacy en `transpilers/`

Este archivo es un inventario histórico interno: no define contrato público ni
habilita backends retirados en CLI, GUI, documentación principal o runtime
normal.

## Contrato público activo

- `registry.py`, `targets.py`, `config/transpile_targets.py` y la política de
  arquitectura exponen únicamente `python`, `javascript` y `rust` como
  backends oficiales activos.
- Los alias cortos `py`, `js` y `node` se tratan como nombres retirados: pueden
  aparecer en mensajes de migración/rechazo, pero no se aceptan como targets
  públicos.

## Compatibilidad interna

- `target_utils.py` conserva listas de nombres retirados o ambiguos para
  construir diagnósticos y recomendaciones de migración, sin normalizarlos a
  targets válidos.
- `module_map.py` y utilidades de runtime validan contra `OFFICIAL_TARGETS` y
  rechazan cualquier backend fuera del contrato activo.

## Snapshots históricos

- `runtime_api_parity_snapshot.json` mantiene la matriz viva en
  `backend_runtime_api` solo para `python`, `javascript` y `rust`.
- Las entradas retiradas (`wasm`, `go`, `cpp`, `java`, `asm`) viven en
  `historical_backend_runtime_api` para comparación histórica y no se consumen
  al construir la matriz activa.
- `_historical_library_compatibility.py` conserva compatibilidad histórica de
  librerías para auditoría/migración y no se exporta desde la matriz oficial.
- `transpiler/historical/wasm_runtime.py` conserva el runtime WASM retirado
  como referencia host-managed histórica; no se importa en startup normal.

## Pruebas y regresión

- Las pruebas pueden mencionar backends legacy cuando verifican rechazo,
  migración, regresiones históricas o compatibilidad interna explícita.
- Cualquier fixture que represente backends retirados debe nombrarse como
  histórico, legacy, retired o rechazo para evitar confusión con el contrato
  activo.

## Código muerto o no permitido

- Referencias legacy en registros públicos, choices de CLI/GUI o documentación
  principal no histórica se consideran código muerto/exposición pública
  accidental.
- `scripts/ci/audit_public_backend_exposure_terms.py` debe fallar si `go`,
  `cpp`, `java`, `wasm`, `asm`, `py`, `js`, `node`, `golang` o `jvm` reaparecen
  en esas superficies públicas sin contexto histórico autorizado.
