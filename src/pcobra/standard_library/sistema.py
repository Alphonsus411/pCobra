"""Fachada de sistema con nombres canónicos en español."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterable

from pcobra.corelibs import sistema as _sistema

__all__ = [
    "obtener_os",
    "ejecutar",
    "ejecutar_async",
    "ejecutar_stream",
    "obtener_env",
    "listar_dir",
    "directorio_actual",

    "ejecutar_comando_async",]


def obtener_os() -> str:
    return _sistema.obtener_os()


def ejecutar(comando: list[str], permitidos: Iterable[str] | None = None, timeout: int | float | None = None) -> str:
    return _sistema.ejecutar(comando, permitidos=permitidos, timeout=timeout)


async def ejecutar_async(comando: list[str], permitidos: Iterable[str] | None = None, timeout: int | float | None = None) -> str:
    return await _sistema.ejecutar_async(comando, permitidos=permitidos, timeout=timeout)


async def ejecutar_stream(comando: list[str], permitidos: Iterable[str] | None = None, timeout: int | float | None = None) -> AsyncIterator[str]:
    async for linea in _sistema.ejecutar_stream(comando, permitidos=permitidos, timeout=timeout):
        yield linea


def obtener_env(nombre: str, por_defecto: str | None = None) -> str | None:
    return _sistema.obtener_env(nombre, por_defecto=por_defecto)


def listar_dir(ruta: str = ".") -> list[str]:
    return _sistema.listar_dir(ruta)


def directorio_actual() -> str:
    return _sistema.directorio_actual()


def ejecutar_comando_async(*args, **kwargs):
    """Delega en ``pcobra.corelibs.sistema.ejecutar_comando_async``."""

    return _sistema.ejecutar_comando_async(*args, **kwargs)
