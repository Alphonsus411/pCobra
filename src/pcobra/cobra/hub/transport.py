"""Contratos mínimos de transporte usados por el repositorio HTTP."""

from __future__ import annotations

from typing import Any, Protocol


class HttpSession(Protocol):
    """Sesión capaz de efectuar las operaciones HTTP requeridas por CobraHub."""

    def get(self, url: str, **kwargs: Any) -> Any: ...

    def post(self, url: str, **kwargs: Any) -> Any: ...


class CobraHubTransport(Protocol):
    """Configuración mínima que el repositorio necesita de un cliente HTTP."""

    base_url: str
    session: HttpSession
    CONNECT_TIMEOUT: float
    READ_TIMEOUT: float
    MAX_FILE_SIZE: int
    CHUNK_SIZE: int


__all__ = ["CobraHubTransport", "HttpSession"]
