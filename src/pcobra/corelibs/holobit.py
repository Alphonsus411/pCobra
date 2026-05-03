"""Adaptador público de Holobit para `usar "holobit"`.

Este módulo expone únicamente funciones serializables y compatibles con Cobra.
No re-exporta clases ni símbolos internos de `pcobra.core.holobits` ni de
`holobit_sdk`.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from typing import Any

from pcobra.core.holobits.holobit import Holobit as _Holobit


def _es_numero(valor: Any) -> bool:
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _normalizar_valores(valores: Iterable[Any]) -> list[float]:
    if isinstance(valores, (str, bytes)):
        raise TypeError("'valores' debe ser una colección numérica, no texto")
    salida: list[float] = []
    for item in valores:
        if not _es_numero(item):
            raise TypeError("Todos los valores del holobit deben ser numéricos")
        salida.append(float(item))
    return salida


def _a_estructura_cobra(hb: _Holobit) -> dict[str, Any]:
    return {"__cobra_tipo__": "holobit", "valores": [float(v) for v in hb.valores]}


def _desde_estructura_cobra(hb: dict[str, Any]) -> _Holobit:
    if not isinstance(hb, dict) or hb.get("__cobra_tipo__") != "holobit":
        raise TypeError("Se esperaba una estructura Cobra de holobit")
    return _Holobit(_normalizar_valores(hb.get("valores", [])))


def crear_holobit(valores: Iterable[Any]) -> dict[str, Any]:
    return _a_estructura_cobra(_Holobit(_normalizar_valores(valores)))


def validar_holobit(hb: Any) -> bool:
    try:
        _desde_estructura_cobra(hb)
    except (TypeError, ValueError):
        return False
    return True


def serializar_holobit(hb: dict[str, Any]) -> str:
    return json.dumps(_desde_estructura_cobra(hb).valores)


def deserializar_holobit(payload: str) -> dict[str, Any]:
    datos = json.loads(payload)
    if not isinstance(datos, Sequence) or isinstance(datos, (str, bytes)):
        raise TypeError("El payload de holobit debe representar una lista")
    return crear_holobit(datos)


def proyectar(hb: dict[str, Any], modo: str) -> dict[str, Any]:
    interno = _desde_estructura_cobra(hb)
    modo_normalizado = str(modo).strip().lower()
    valores = list(interno.valores)
    if modo_normalizado in {"1d", "linea"}:
        salida = valores[:1]
    elif modo_normalizado in {"2d", "plano"}:
        salida = (valores + [0.0, 0.0])[:2]
    elif modo_normalizado in {"3d", "espacio"}:
        salida = (valores + [0.0, 0.0, 0.0])[:3]
    elif modo_normalizado == "vector":
        salida = valores
    else:
        raise ValueError(f"Modo de proyección no soportado: {modo}")
    return crear_holobit(salida)


def transformar(hb: dict[str, Any], operacion: str, *parametros: Any) -> dict[str, Any]:
    interno = _desde_estructura_cobra(hb)
    if operacion == "rotar" and len(parametros) >= 2:
        eje = str(parametros[0]).lower()
        angulo = float(parametros[1])
        factor = angulo / 360.0
        nuevos = list(interno.valores)
        if nuevos:
            if eje == "x":
                nuevos[0] += factor
            elif eje == "y" and len(nuevos) > 1:
                nuevos[1] += factor
            elif eje == "z" and len(nuevos) > 2:
                nuevos[2] += factor
        interno = _Holobit(nuevos)
    else:
        raise ValueError(f"Operación no soportada: {operacion}")
    return _a_estructura_cobra(interno)


def graficar(hb: dict[str, Any]) -> str:
    interno = _desde_estructura_cobra(hb)
    return f"Holobit({interno.valores})"


def combinar(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    ha = _desde_estructura_cobra(a)
    hb = _desde_estructura_cobra(b)
    return crear_holobit([*ha.valores, *hb.valores])


def medir(hb: dict[str, Any]) -> dict[str, float | int]:
    interno = _desde_estructura_cobra(hb)
    valores = interno.valores
    magnitud = sum(v * v for v in valores) ** 0.5
    return {"dimension": len(valores), "magnitud": float(magnitud)}



__all__ = [
    "crear_holobit",
    "validar_holobit",
    "serializar_holobit",
    "deserializar_holobit",
    "proyectar",
    "transformar",
    "graficar",
    "combinar",
    "medir",
]
