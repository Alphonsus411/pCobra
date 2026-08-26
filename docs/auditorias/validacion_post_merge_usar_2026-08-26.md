# Validación post-merge del contrato público de `usar`

Fecha de ejecución: 2026-08-26.

## Revisiones comparadas

- `HEAD` post-merge: `a1560d0bcd6b367632bdceb0a3cd553e7376e377`.
- Primer padre (`HEAD^1`): `b8ba487afd883f72de2a22fb5ecfed875e755357`.
- Las comparaciones aisladas se ejecutaron en worktrees temporales *detached* y
  ambos worktrees se eliminaron al terminar.

## Verificaciones sobre el `HEAD` post-merge

| Comando | Código de salida | Resultado |
|---|---:|---|
| `python -m compileall -q src` | 0 | Correcto |
| `python scripts/validate_runtime_contract.py` | 0 | Contrato runtime correcto |
| `python scripts/sync_libro_programacion.py --check` | 0 | Sin drift documental |
| `python -m pytest -q tests/unit/test_usar_public_contract.py tests/integration/test_usar_public_contract_regression.py tests/integration/test_repl_usar_entrypoints_contract.py` | 1 | 2 fallos, 143 pruebas correctas y 2 avisos |

## Node IDs fallidos y comparación aislada

| Node ID exacto | `HEAD^1` | `HEAD` post-merge | Clasificación |
|---|---:|---:|---|
| `tests/integration/test_usar_public_contract_regression.py::test_conflicto_no_overwrite_silencioso_reporta_error_estructurado` | 1 | 1 | `HISTORICAL_BASELINE` |
| `tests/integration/test_usar_public_contract_regression.py::test_conflictos_abortan_inyeccion_sin_overwrite_silencioso` | 1 | 1 | `HISTORICAL_BASELINE` |

En los cuatro casos aislados, `pytest` informó un único fallo. La manera del
fallo fue la misma en ambos árboles: la aserción esperaba que el `NameError`
coincidiera con `usar_error\[conflicto_simbolo\]`, pero el mensaje real comenzó
con `No se puede usar 'datos': hay conflicto de símbolos en el contexto actual`
y conservó la misma colisión estructurada para el símbolo `filtrar` del módulo
`datos` en fase `preflight`.

## Decisión de publicación

No se detectó ningún `NEW_REGRESSION`: ninguno de los node IDs pasa en
`HEAD^1` y falla sólo después del merge. Los dos fallos observados son
`HISTORICAL_BASELINE`, por lo que esta auditoría no modifica código, pruebas,
aserciones, `skip` ni `xfail`, y no bloquea la publicación por una regresión
nueva.
