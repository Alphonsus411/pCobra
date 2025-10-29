"""Funciones para graficar objetos ``Holobit`` utilizando ``holobit-sdk``."""

from __future__ import annotations

import sys
from types import ModuleType
from typing import Iterable

import numpy as np

from .holobit import Holobit

_MISSING_HOLOBIT_ERROR: ModuleNotFoundError | None = None

try:  # pragma: no branch - dependencia opcional
    from holobit_sdk.visualization.projector import proyectar_holograma
    from holobit_sdk.core.quark import Quark
    from holobit_sdk.core.holobit import Holobit as SDKHolobit
except ModuleNotFoundError as exc:  # pragma: no cover - entorno mínimo
    _MISSING_HOLOBIT_ERROR = exc

    def _registrar_modulo(nombre: str) -> ModuleType:
        modulo = sys.modules.get(nombre)
        if modulo is None:
            modulo = ModuleType(nombre)
            sys.modules[nombre] = modulo
        return modulo

    _sdk_mod = _registrar_modulo("holobit_sdk")
    _sdk_mod.__path__ = []  # type: ignore[attr-defined]
    _core_mod = getattr(_sdk_mod, "core", None)
    if _core_mod is None:
        _core_mod = ModuleType("holobit_sdk.core")
        _sdk_mod.core = _core_mod
        sys.modules["holobit_sdk.core"] = _core_mod
    _core_mod.__path__ = []  # type: ignore[attr-defined]

    _viz_mod = getattr(_sdk_mod, "visualization", None)
    if _viz_mod is None:
        _viz_mod = ModuleType("holobit_sdk.visualization")
        _sdk_mod.visualization = _viz_mod
        sys.modules["holobit_sdk.visualization"] = _viz_mod
    _viz_mod.__path__ = []  # type: ignore[attr-defined]

    _projector_mod = ModuleType("holobit_sdk.visualization.projector")
    sys.modules["holobit_sdk.visualization.projector"] = _projector_mod
    _viz_mod.projector = _projector_mod

    def proyectar_holograma(_hb: "SDKHolobit") -> None:  # type: ignore[override]
        raise ModuleNotFoundError(
            "Las funciones de holobits requieren la dependencia opcional 'holobit_sdk'."
        ) from _MISSING_HOLOBIT_ERROR

    _projector_mod.proyectar_holograma = proyectar_holograma

    class Quark:  # type: ignore[no-redef]
        """Quark mínimo utilizado cuando ``holobit_sdk`` no está disponible."""

        def __init__(self, valor: float, x: float, y: float, z: float = 0.0) -> None:
            self.valor = float(valor)
            self.posicion = np.array([float(x), float(y), float(z)], dtype=float)

    _quark_mod = ModuleType("holobit_sdk.core.quark")
    _quark_mod.Quark = Quark
    sys.modules["holobit_sdk.core.quark"] = _quark_mod
    _core_mod.quark = _quark_mod

    class SDKHolobit:  # type: ignore[no-redef]
        """Implementación básica para escenarios sin ``holobit_sdk``."""

        def __init__(
            self, quarks: Iterable[Quark], antiquarks: Iterable[Quark]
        ) -> None:
            self.quarks = [*quarks]
            self.antiquarks = [*antiquarks]

        def rotar(self, *_args, **_kwargs) -> None:  # pragma: no cover - simple
            raise ModuleNotFoundError(
                "La rotación de holobits requiere la dependencia opcional 'holobit_sdk'."
            ) from _MISSING_HOLOBIT_ERROR

    _holobit_mod = ModuleType("holobit_sdk.core.holobit")
    _holobit_mod.Holobit = SDKHolobit
    sys.modules["holobit_sdk.core.holobit"] = _holobit_mod
    _core_mod.holobit = _holobit_mod

    _HOLOBIT_SDK_ERROR = _MISSING_HOLOBIT_ERROR
else:  # pragma: no cover - entorno con dependencia instalada
    _HOLOBIT_SDK_ERROR = None


def _to_sdk_holobit(hb: Holobit) -> SDKHolobit:
    """Convierte un :class:`Holobit` local a uno del SDK."""
    valores = list(hb.valores) + [0.0] * (6 - len(hb.valores))
    quarks = [Quark(v, 0, 0) for v in valores[:6]]
    antiquarks = [Quark(-q.posicion[0], -q.posicion[1], -q.posicion[2]) for q in quarks]
    return SDKHolobit(quarks, antiquarks)


def graficar(hb: Holobit):
    """Grafica un ``Holobit`` delegando en ``holobit-sdk``."""
    if not isinstance(hb, Holobit):
        raise TypeError("graficar espera una instancia de Holobit")
    sdk_hb = _to_sdk_holobit(hb)
    proyectar_holograma(sdk_hb)
    return None
