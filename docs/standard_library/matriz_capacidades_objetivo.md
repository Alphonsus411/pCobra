# Matriz de capacidades objetivo (cobra-facing)

| Módulo | API pública (español) | Equivalencia semántica inspiración Python |
|---|---|---|
| numero | Ver `CAPACIDADES_POR_MODULO['numero']['api_canonica']` | `math` + builtins numéricos |
| texto | Ver `CAPACIDADES_POR_MODULO['texto']['api_canonica']` | métodos `str` y utilidades unicode |
| datos | Ver `CAPACIDADES_POR_MODULO['datos']['api_canonica']` | `csv/json/functools` (sin exponer backend) |
| logica | Ver `CAPACIDADES_POR_MODULO['logica']['api_canonica']` | `all/any/bool` |
| asincrono | Ver `CAPACIDADES_POR_MODULO['asincrono']['api_canonica']` | `asyncio` |
| sistema | Ver `CAPACIDADES_POR_MODULO['sistema']['api_canonica']` | `os/subprocess` |
| archivo | Ver `CAPACIDADES_POR_MODULO['archivo']['api_canonica']` | `open/pathlib` |
| tiempo | Ver `CAPACIDADES_POR_MODULO['tiempo']['api_canonica']` | `time/datetime` |
| red | Ver `CAPACIDADES_POR_MODULO['red']['api_canonica']` | `urllib/requests` conceptual |
| holobit | Ver `CAPACIDADES_POR_MODULO['holobit']['api_canonica']` | serialización/transformación de colecciones |

Fuente canónica: `src/pcobra/contrato_capacidades_corelibs.py`.
