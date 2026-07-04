"""Utilidades de rutas para la biblioteca estándar de Cobra."""

import os
from pathlib import Path
from typing import Union

PathLike = Union[str, os.PathLike[str]]

__all__ = [
    "unir",
    "normalizar",
    "nombre",
    "extension",
    "padre",
    "existe",
    "es_absoluta",
    "absoluta",
    "relativa",
]


def _validar_ruta(ruta: PathLike, nombre_argumento: str = "ruta") -> PathLike:
    if not isinstance(ruta, (str, os.PathLike)):
        raise TypeError(
            f"{nombre_argumento} debe ser una ruta de texto o compatible con os.PathLike"
        )
    texto = os.fspath(ruta)
    if not isinstance(texto, str):
        raise TypeError(f"{nombre_argumento} debe representar una ruta de texto")
    if texto == "":
        raise ValueError(f"{nombre_argumento} no puede estar vacía")
    return ruta


def unir(*partes: PathLike) -> str:
    """Une segmentos de ruta y devuelve la ruta resultante como texto."""

    if not partes:
        raise ValueError("partes debe contener al menos una ruta")
    partes_validadas = tuple(
        _validar_ruta(parte, f"partes[{indice}]") for indice, parte in enumerate(partes)
    )
    return str(Path(partes_validadas[0]).joinpath(*partes_validadas[1:]))


def normalizar(ruta: PathLike) -> str:
    """Normaliza separadores y componentes redundantes de una ruta."""

    ruta_validada = _validar_ruta(ruta)
    return os.path.normpath(os.fspath(ruta_validada))


def nombre(ruta: PathLike) -> str:
    """Devuelve el nombre final de una ruta."""

    ruta_validada = _validar_ruta(ruta)
    return Path(ruta_validada).name


def extension(ruta: PathLike) -> str:
    """Devuelve la extensión final de una ruta, incluyendo el punto si existe."""

    ruta_validada = _validar_ruta(ruta)
    return Path(ruta_validada).suffix


def padre(ruta: PathLike) -> str:
    """Devuelve el directorio padre de una ruta como texto."""

    ruta_validada = _validar_ruta(ruta)
    return str(Path(ruta_validada).parent)


def existe(ruta: PathLike) -> bool:
    """Indica si una ruta existe en el sistema de archivos."""

    ruta_validada = _validar_ruta(ruta)
    return Path(ruta_validada).exists()


def es_absoluta(ruta: PathLike) -> bool:
    """Indica si una ruta es absoluta."""

    ruta_validada = _validar_ruta(ruta)
    return Path(ruta_validada).is_absolute()


def absoluta(ruta: PathLike) -> str:
    """Devuelve la versión absoluta de una ruta sin exigir que exista."""

    ruta_validada = _validar_ruta(ruta)
    return str(Path(ruta_validada).absolute())


def relativa(ruta: PathLike, base: PathLike = ".") -> str:
    """Devuelve ``ruta`` relativa a ``base``."""

    ruta_validada = _validar_ruta(ruta)
    base_validada = _validar_ruta(base, "base")
    return os.path.relpath(os.fspath(ruta_validada), os.fspath(base_validada))
