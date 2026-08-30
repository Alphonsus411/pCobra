"""Contratos internos e inmutables de capacidades para ``usar``."""

from __future__ import annotations

from enum import StrEnum


class CapacidadUsar(StrEnum):
    PROCESS_SPAWN = "process.spawn"
    PROCESS_SHELL = "process.shell"
    NETWORK_GET = "network.get"
    NETWORK_POST = "network.post"
    NETWORK_DOWNLOAD = "network.download"
    FILESYSTEM_WRITE = "filesystem.write"
    FILESYSTEM_READ = "filesystem.read"
    ASYNC_SCHEDULE = "async.schedule"
    CLOCK_READ = "clock.read"
    CLOCK_SLEEP = "clock.sleep"
    ENVIRONMENT_READ = "environment.read"
    LOGGING_WRITE = "logging.write"
    RANDOM_READ = "random.read"


def simbolo_canonico(modulo: str, nombre: str) -> tuple[str, str]:
    """Resuelve la identidad documental sin mantener otra tabla de capacidades."""

    from pcobra.cobra.usar_policy import CANONICAL_MODULE_SURFACE_CONTRACTS

    aliases_semanticos = {
        ("red", "obtener_url_async"): "obtener_url",
        ("red", "enviar_post_async"): "enviar_post",
        ("red", "obtener_json"): "obtener_url",
    }
    contract = CANONICAL_MODULE_SURFACE_CONTRACTS.get(modulo)
    target = aliases_semanticos.get((modulo, nombre), nombre)
    if contract is not None:
        target = contract.allowed_aliases.get(nombre, target)
    return modulo, target


def capacidades_de(modulo: str, nombre: str) -> frozenset[CapacidadUsar]:
    """Consulta directamente la clasificación canónica de ``usar_policy``."""

    from pcobra.cobra.usar_policy import CANONICAL_MODULE_SURFACE_CONTRACTS

    contract = CANONICAL_MODULE_SURFACE_CONTRACTS.get(modulo)
    if contract is None:
        return frozenset()
    return frozenset(
        CapacidadUsar(capability)
        for capability in contract.symbol_capabilities.get(nombre, frozenset())
    )
