"""Adaptador público de Holobit para `usar "holobit"`.

Este módulo expone únicamente funciones serializables y compatibles con Cobra.
No re-exporta clases ni símbolos internos de `pcobra.core.holobits` ni de
`holobit_sdk`.
"""

import json
from collections.abc import Iterable, Sequence
from typing import Any

from pcobra.core.holobits.graficar import graficar as _sdk_graficar
from pcobra.core.holobits.holobit import Holobit as _SDKHolobit


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


def _a_estructura_cobra(hb: _SDKHolobit) -> dict[str, Any]:
    return {"tipo": "holobit", "valores": [float(v) for v in hb.valores]}


def _desde_estructura_cobra(hb: dict[str, Any]) -> _SDKHolobit:
    if not isinstance(hb, dict) or hb.get("tipo") != "holobit":
        raise TypeError("Se esperaba una estructura Cobra de holobit")
    return _SDKHolobit(_normalizar_valores(hb.get("valores", [])))


def crear_holobit(valores: Iterable[Any]) -> dict[str, Any]:
    return _a_estructura_cobra(_SDKHolobit(_normalizar_valores(valores)))


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
    valores = list(interno.valores)
    modo_norm = str(modo).strip().lower()
    if modo_norm == "2d":
        return crear_holobit(valores[:2])
    if modo_norm == "3d":
        return crear_holobit(valores[:3])
    raise ValueError("Modo de proyección no soportado")


def transformar(hb: dict[str, Any], operacion: str, *parametros: Any) -> dict[str, Any]:
    valores = list(_desde_estructura_cobra(hb).valores)
    op = str(operacion).strip().lower()
    if op == "rotar":
        if len(parametros) < 2:
            raise ValueError("rotar requiere eje y ángulo")
        eje = str(parametros[0]).strip().lower()
        angulo = float(parametros[1])
        if eje != "z" or len(valores) < 2:
            return crear_holobit(valores)
        import math

        rad = math.radians(angulo)
        x, y = valores[0], valores[1]
        valores[0] = x * math.cos(rad) - y * math.sin(rad)
        valores[1] = x * math.sin(rad) + y * math.cos(rad)
        return crear_holobit(valores)

    raise ValueError(f"Operacion no soportada: {operacion}")


def graficar(hb: dict[str, Any]) -> str:
    return _sdk_graficar(_desde_estructura_cobra(hb))


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

del Any, Iterable, Sequence
