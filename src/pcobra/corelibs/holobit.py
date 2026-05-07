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


class ErrorHolobit(ValueError):
    """Error de dominio Cobra para operaciones de Holobit."""


def _error_dominio(mensaje: str, *, causa: Exception | None = None) -> ErrorHolobit:
    if causa is None:
        return ErrorHolobit(mensaje)
    return ErrorHolobit(mensaje)


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


def _validar_estructura_holobit(hb: Any) -> dict[str, Any]:
    if not isinstance(hb, dict):
        raise TypeError("El holobit debe ser un objeto tipo dict")
    claves = set(hb.keys())
    if claves != {"tipo", "valores"}:
        raise TypeError("Las claves permitidas del holobit son exactamente: tipo, valores")
    if hb["tipo"] != "holobit":
        raise TypeError("La clave 'tipo' debe ser la cadena 'holobit'")
    valores = hb["valores"]
    if not isinstance(valores, Sequence) or isinstance(valores, (str, bytes)):
        raise TypeError("La clave 'valores' debe ser una lista o secuencia numérica")
    return hb


def _desde_estructura_cobra(hb: dict[str, Any]) -> _SDKHolobit:
    estructura = _validar_estructura_holobit(hb)
    try:
        return _SDKHolobit(_normalizar_valores(estructura["valores"]))
    except Exception as exc:  # pragma: no cover - defensivo frente al SDK
        raise _error_dominio("No se pudo adaptar el holobit al runtime de Cobra", causa=exc) from None


def crear_holobit(valores: Iterable[Any]) -> dict[str, Any]:
    if valores is None:
        raise TypeError("'valores' no puede ser None")
    return _a_estructura_cobra(_SDKHolobit(_normalizar_valores(valores)))


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
    try:
        datos = json.loads(payload)
    except json.JSONDecodeError:
        raise _error_dominio("El payload de holobit no es JSON válido") from None
    _validar_estructura_holobit(datos)
    return crear_holobit(datos["valores"])


def proyectar(hb: dict[str, Any], modo: str) -> dict[str, Any]:
    if not isinstance(modo, str):
        raise TypeError("'modo' debe ser texto")
    interno = _desde_estructura_cobra(hb)
    valores = list(interno.valores)
    modo_norm = modo.strip().lower()
    if modo_norm == "2d":
        return crear_holobit(valores[:2])
    if modo_norm == "3d":
        return crear_holobit(valores[:3])
    raise ValueError("Modo de proyección no soportado")


def transformar(hb: dict[str, Any], operacion: str, *parametros: Any) -> dict[str, Any]:
    if not isinstance(operacion, str):
        raise TypeError("'operacion' debe ser texto")
    valores = list(_desde_estructura_cobra(hb).valores)
    op = operacion.strip().lower()
    if op == "rotar":
        if len(parametros) < 2:
            raise ValueError("rotar requiere eje y ángulo")
        eje = str(parametros[0]).strip().lower()
        if not _es_numero(parametros[1]):
            raise TypeError("El ángulo de rotación debe ser numérico")
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
    try:
        vista = _sdk_graficar(_desde_estructura_cobra(hb))
    except Exception as exc:  # pragma: no cover - defensivo frente al SDK
        raise _error_dominio("No se pudo graficar el holobit en el runtime de Cobra", causa=exc) from None
    if not isinstance(vista, str):
        raise TypeError("La salida de graficar debe ser texto")
    return vista


def combinar(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    ha = _desde_estructura_cobra(a)
    hb = _desde_estructura_cobra(b)
    return crear_holobit([*ha.valores, *hb.valores])


def medir(hb: dict[str, Any]) -> dict[str, float | int]:
    interno = _desde_estructura_cobra(hb)
    valores = interno.valores
    magnitud = sum(v * v for v in valores) ** 0.5
    salida = {"dimension": len(valores), "magnitud": float(magnitud)}
    if not isinstance(salida["dimension"], int) or not _es_numero(salida["magnitud"]):
        raise TypeError("Salida inválida de medir")
    return salida


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

