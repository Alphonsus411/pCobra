"""Contratos internos e inmutables de capacidades para ``usar``."""

from __future__ import annotations

from enum import StrEnum
from types import MappingProxyType


class CapacidadUsar(StrEnum):
    PROCESS_SPAWN = "process.spawn"
    PROCESS_SHELL = "process.shell"
    NETWORK_GET = "network.get"
    NETWORK_POST = "network.post"
    NETWORK_DOWNLOAD = "network.download"
    FILESYSTEM_WRITE = "filesystem.write"


_SIMBOLO_CANONICO = MappingProxyType(
    {
        ("proceso", "ejecutar"): ("proceso", "ejecutar"),
        ("proceso", "capturar"): ("proceso", "ejecutar"),
        ("proceso", "ejecutar_async"): ("proceso", "ejecutar_async"),
        ("proceso", "ejecutar_stream"): ("proceso", "ejecutar_stream"),
        ("red", "obtener_url"): ("red", "obtener_url"),
        ("red", "obtener_url_async"): ("red", "obtener_url"),
        ("red", "obtener_url_texto"): ("red", "obtener_url"),
        ("red", "obtener_json"): ("red", "obtener_url"),
        ("red", "enviar_post"): ("red", "enviar_post"),
        ("red", "enviar_post_async"): ("red", "enviar_post"),
        ("red", "descargar_archivo"): ("red", "descargar_archivo"),
    }
)

_CAPACIDADES = MappingProxyType(
    {
        ("proceso", "ejecutar"): frozenset({CapacidadUsar.PROCESS_SPAWN}),
        ("proceso", "ejecutar_async"): frozenset({CapacidadUsar.PROCESS_SPAWN}),
        ("proceso", "ejecutar_stream"): frozenset({CapacidadUsar.PROCESS_SPAWN}),
        ("red", "obtener_url"): frozenset({CapacidadUsar.NETWORK_GET}),
        ("red", "enviar_post"): frozenset({CapacidadUsar.NETWORK_POST}),
        ("red", "descargar_archivo"): frozenset(
            {CapacidadUsar.NETWORK_DOWNLOAD, CapacidadUsar.FILESYSTEM_WRITE}
        ),
    }
)


def simbolo_canonico(modulo: str, nombre: str) -> tuple[str, str]:
    """Resuelve aliases sin consultar atributos del objeto exportado."""

    return _SIMBOLO_CANONICO.get((modulo, nombre), (modulo, nombre))


def capacidades_de(modulo: str, nombre: str) -> frozenset[CapacidadUsar]:
    """Devuelve el contrato mantenido por código para el símbolo canónico."""

    return _CAPACIDADES.get(simbolo_canonico(modulo, nombre), frozenset())
