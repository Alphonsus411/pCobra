"""Utilidades de registro para las corelibs de Cobra.

El módulo encapsula :mod:`logging` detrás de una API pequeña en español y usa
un registrador propio para evitar modificar el registrador raíz de Python.
"""

from __future__ import annotations

import logging
from os import PathLike
from pathlib import Path
from typing import TextIO

_NOMBRE_BASE = "pcobra.registro"
_FORMATO_DEFECTO = "%(levelname)s:%(name)s:%(message)s"

__all__ = [
    "configurar",
    "debug",
    "info",
    "aviso",
    "error",
    "obtener_registrador",
]


RegistradorDestino = str | PathLike[str] | TextIO | None


_REGISTRADOR = logging.getLogger(_NOMBRE_BASE)
_REGISTRADOR.addHandler(logging.NullHandler())
_REGISTRADOR.propagate = False


def _normalizar_nivel(nivel: str | int) -> int:
    """Convierte un nivel de logging textual o numérico a su valor entero."""

    if isinstance(nivel, str):
        nombre_nivel = nivel.upper()
        valor = logging.getLevelName(nombre_nivel)
        if isinstance(valor, int):
            return valor
        niveles_validos = ", ".join(logging.getLevelNamesMapping())
        raise ValueError(
            f"Nivel de registro inválido: {nivel!r}. "
            f"Use uno de: {niveles_validos}, o un entero compatible con logging."
        )

    if isinstance(nivel, int):
        return nivel

    raise TypeError(
        "nivel debe ser una cadena como 'INFO' o un entero compatible con logging"
    )


def _crear_manejador(destino: RegistradorDestino) -> logging.Handler:
    """Crea un manejador hacia stderr, archivo o flujo explícito."""

    if destino is None:
        return logging.StreamHandler()

    if hasattr(destino, "write"):
        return logging.StreamHandler(destino)  # type: ignore[arg-type]

    return logging.FileHandler(Path(destino), encoding="utf-8")


def configurar(
    *,
    nivel: str | int = "INFO",
    formato: str | None = None,
    destino: RegistradorDestino = None,
) -> logging.Logger:
    """Configura y devuelve el registrador propio de Cobra.

    Args:
        nivel: Nivel de logging textual (por ejemplo ``"INFO"``) o entero.
        formato: Formato para los mensajes. Si es ``None`` se usa un formato
            simple con nivel, nombre del registrador y mensaje.
        destino: ``None`` para stderr, una ruta explícita para archivo, o un
            flujo compatible con ``write``.

    Raises:
        ValueError: si ``nivel`` no es un nivel reconocido por ``logging``.
        TypeError: si ``nivel`` o ``destino`` no tienen tipos compatibles.
    """

    nivel_normalizado = _normalizar_nivel(nivel)
    manejador = _crear_manejador(destino)
    manejador.setLevel(nivel_normalizado)
    manejador.setFormatter(logging.Formatter(formato or _FORMATO_DEFECTO))

    _REGISTRADOR.handlers.clear()
    _REGISTRADOR.addHandler(manejador)
    _REGISTRADOR.setLevel(nivel_normalizado)
    _REGISTRADOR.propagate = False
    return _REGISTRADOR


def obtener_registrador(nombre: str = "cobra") -> logging.Logger:
    """Devuelve un registrador bajo el espacio de nombres propio del módulo."""

    if not isinstance(nombre, str):
        raise TypeError("nombre debe ser una cadena")

    nombre_limpio = nombre.strip()
    if not nombre_limpio or nombre_limpio == "cobra":
        return _REGISTRADOR

    if nombre_limpio == _NOMBRE_BASE or nombre_limpio.startswith(f"{_NOMBRE_BASE}."):
        return logging.getLogger(nombre_limpio)

    return logging.getLogger(f"{_NOMBRE_BASE}.{nombre_limpio}")


def debug(mensaje: object) -> None:
    """Registra ``mensaje`` con nivel DEBUG."""

    _REGISTRADOR.debug(mensaje)


def info(mensaje: object) -> None:
    """Registra ``mensaje`` con nivel INFO."""

    _REGISTRADOR.info(mensaje)


def aviso(mensaje: object) -> None:
    """Registra ``mensaje`` con nivel WARNING."""

    _REGISTRADOR.warning(mensaje)


def error(mensaje: object) -> None:
    """Registra ``mensaje`` con nivel ERROR."""

    _REGISTRADOR.error(mensaje)
