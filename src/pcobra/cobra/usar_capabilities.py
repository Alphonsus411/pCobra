"""Contratos internos e inmutables de capacidades para ``usar``."""

from __future__ import annotations

from enum import StrEnum
from types import MappingProxyType


class CapacidadUsar(StrEnum):
    PROCESS_SPAWN = "process.spawn"
    PROCESS_SHELL = "process.shell"


_SIMBOLO_CANONICO = MappingProxyType(
    {
        ("proceso", "ejecutar"): ("proceso", "ejecutar"),
        ("proceso", "capturar"): ("proceso", "ejecutar"),
        ("proceso", "ejecutar_async"): ("proceso", "ejecutar_async"),
        ("proceso", "ejecutar_stream"): ("proceso", "ejecutar_stream"),
    }
)

_CAPACIDADES = MappingProxyType(
    {
        ("proceso", "ejecutar"): frozenset({CapacidadUsar.PROCESS_SPAWN}),
        ("proceso", "ejecutar_async"): frozenset({CapacidadUsar.PROCESS_SPAWN}),
        ("proceso", "ejecutar_stream"): frozenset({CapacidadUsar.PROCESS_SPAWN}),
    }
)


def simbolo_canonico(modulo: str, nombre: str) -> tuple[str, str]:
    """Resuelve aliases sin consultar atributos del objeto exportado."""

    return _SIMBOLO_CANONICO.get((modulo, nombre), (modulo, nombre))


def capacidades_de(modulo: str, nombre: str) -> frozenset[CapacidadUsar]:
    """Devuelve el contrato mantenido por código para el símbolo canónico."""

    return _CAPACIDADES.get(simbolo_canonico(modulo, nombre), frozenset())
