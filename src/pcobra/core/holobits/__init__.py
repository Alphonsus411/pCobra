"""Superficie pública saneada para Holobit en runtime Python."""

from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from typing import Any

from .graficar import graficar as _graficar_sdk
from .holobit import Holobit as _Holobit
from .proyeccion import proyectar as _proyectar_sdk
from .transformacion import transformar as _transformar_sdk

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
    return {"tipo": "holobit", "valores": [float(v) for v in hb.valores]}


def _validar_estructura_holobit(hb: Any) -> dict[str, Any]:
    if not isinstance(hb, dict):
        raise TypeError("El holobit debe ser un objeto tipo dict")
    if set(hb.keys()) != {"tipo", "valores"}:
        raise TypeError("Las claves permitidas del holobit son exactamente: tipo, valores")
    if hb["tipo"] != "holobit":
        raise TypeError("La clave 'tipo' debe ser la cadena 'holobit'")
    valores = hb["valores"]
    if not isinstance(valores, Sequence) or isinstance(valores, (str, bytes)):
        raise TypeError("La clave 'valores' debe ser una lista o secuencia numérica")
    return hb


def _desde_estructura_cobra(hb: dict[str, Any]) -> _Holobit:
    estructura = _validar_estructura_holobit(hb)
    return _Holobit(_normalizar_valores(estructura["valores"]))


def crear_holobit(valores: Iterable[Any]) -> dict[str, Any]:
    if valores is None:
        raise TypeError("'valores' no puede ser None")
    return _a_estructura_cobra(_Holobit(_normalizar_valores(valores)))


def validar_holobit(hb: Any) -> bool:
    try:
        _desde_estructura_cobra(hb)
    except (TypeError, ValueError):
        return False
    return True


def serializar_holobit(hb: dict[str, Any]) -> str:
    return json.dumps(_a_estructura_cobra(_desde_estructura_cobra(hb)), ensure_ascii=False)


def deserializar_holobit(payload: str) -> dict[str, Any]:
    if not isinstance(payload, str):
        raise TypeError("El payload de holobit debe ser texto JSON")
    datos = json.loads(payload)
    _validar_estructura_holobit(datos)
    return crear_holobit(datos["valores"])


def proyectar(hb: dict[str, Any], modo: str) -> dict[str, Any]:
    interno = _desde_estructura_cobra(hb)
    modo_norm = str(modo).strip().lower()
    if modo_norm in {"2d", "3d"}:
        _proyectar_sdk(interno, modo_norm)
        if modo_norm == "2d":
            return crear_holobit(interno.valores[:2])
        return crear_holobit(interno.valores[:3])
    raise ValueError("Modo de proyección no soportado")


def transformar(hb: dict[str, Any], operacion: str, *parametros: Any) -> dict[str, Any]:
    interno = _desde_estructura_cobra(hb)
    _transformar_sdk(interno, operacion, *parametros)

    op = str(operacion).strip().lower()
    if op == "rotar" and len(parametros) >= 2:
        eje = str(parametros[0]).strip().lower()
        angulo = float(parametros[1])
        valores = list(interno.valores)
        if eje == "z" and len(valores) >= 2:
            import math

            rad = math.radians(angulo)
            x, y = valores[0], valores[1]
            valores[0] = x * math.cos(rad) - y * math.sin(rad)
            valores[1] = x * math.sin(rad) + y * math.cos(rad)
            interno = _Holobit(valores)

    return _a_estructura_cobra(interno)


def graficar(hb: dict[str, Any]) -> str:
    _graficar_sdk(_desde_estructura_cobra(hb))
    return ""


def combinar(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    ha = _desde_estructura_cobra(a)
    hb = _desde_estructura_cobra(b)
    return crear_holobit([*ha.valores, *hb.valores])


def medir(hb: dict[str, Any]) -> dict[str, float | int]:
    interno = _desde_estructura_cobra(hb)
    magnitud = sum(v * v for v in interno.valores) ** 0.5
    return {"dimension": len(interno.valores), "magnitud": float(magnitud)}
