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
    "ejecutar_comando_async",
]


def obtener_os() -> str:
    """Retorna el nombre del sistema operativo detectado por el runtime."""
    return _sistema.obtener_os()


def ejecutar(comando: list[str], permitidos: Iterable[str] | None = None, timeout: int | float | None = None) -> str:
    """Ejecuta un comando validando lista blanca y límite de tiempo."""
    return _sistema.ejecutar(comando, permitidos=permitidos, timeout=timeout)


async def ejecutar_async(comando: list[str], permitidos: Iterable[str] | None = None, timeout: int | float | None = None) -> str:
    """Versión asíncrona segura de ``ejecutar`` con lista blanca obligatoria."""
    return await _sistema.ejecutar_async(comando, permitidos=permitidos, timeout=timeout)


async def ejecutar_stream(comando: list[str], permitidos: Iterable[str] | None = None, timeout: int | float | None = None) -> AsyncIterator[str]:
    """Entrega la salida estándar por líneas desde un proceso permitido."""
    async for linea in _sistema.ejecutar_stream(comando, permitidos=permitidos, timeout=timeout):
        yield linea


def obtener_env(nombre: str, por_defecto: str | None = None) -> str | None:
    """Lee una variable de entorno sin exponer objetos internos del backend."""
    return _sistema.obtener_env(nombre, por_defecto=por_defecto)


def listar_dir(ruta: str = ".") -> list[str]:
    """Lista entradas de directorio como cadenas sanitizadas."""
    return _sistema.listar_dir(ruta)


def directorio_actual() -> str:
    """Devuelve la ruta de trabajo actual."""
    return _sistema.directorio_actual()


def ejecutar_comando_async(*args, **kwargs):
    """Alias de compatibilidad para ejecución asíncrona de comandos permitidos."""

    return _sistema.ejecutar_comando_async(*args, **kwargs)
