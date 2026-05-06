"""Funciones básicas para manipular archivos de texto."""

from __future__ import annotations
from pcobra.corelibs import archivo as _archivo

import os
from pathlib import Path
from typing import Union

PathLike = Union[str, os.PathLike[str]]


def _resolver_ruta(ruta: PathLike) -> Path:
    """Normaliza ``ruta`` asegurando que permanezca en un directorio seguro."""

    base = Path(os.environ.get("COBRA_IO_BASE_DIR") or Path.cwd()).resolve()
    objetivo = Path(ruta)
    if objetivo.is_absolute():
        raise ValueError("Las rutas absolutas no están permitidas")
    if ".." in objetivo.parts:
        raise ValueError("La ruta no puede contener '..'")
    destino = (base / objetivo).resolve()
    try:
        destino.relative_to(base)
    except ValueError as exc:
        raise ValueError("La ruta queda fuera del directorio permitido") from exc
    return destino


def leer(ruta: PathLike) -> str:
    """Devuelve el contenido de un archivo dentro del directorio permitido.

    La ruta debe permanecer dentro de ``COBRA_IO_BASE_DIR`` (si existe) o del
    directorio de trabajo actual. Se lanza ``ValueError`` si la ruta no es
    válida.
    """

    ruta_segura = _resolver_ruta(ruta)
    with ruta_segura.open("r", encoding="utf-8") as f:
        return f.read()


def escribir(ruta: PathLike, datos: str) -> None:
    """Sobrescribe el archivo indicado con ``datos`` dentro del directorio permitido.

    La ruta debe permanecer dentro de ``COBRA_IO_BASE_DIR`` (si existe) o del
    directorio de trabajo actual. Se lanza ``ValueError`` si la ruta no es
    válida.
    """

    ruta_segura = _resolver_ruta(ruta)
    with ruta_segura.open("w", encoding="utf-8") as f:
        f.write(datos)


def adjuntar(ruta: PathLike, datos: str) -> None:
    """Agrega ``datos`` al final de un archivo dentro del directorio permitido."""

    ruta_segura = _resolver_ruta(ruta)
    with ruta_segura.open("a", encoding="utf-8") as f:
        f.write(datos)


def existe(ruta: PathLike) -> bool:
    """Indica si el archivo existe dentro del directorio permitido."""

    try:
        ruta_segura = _resolver_ruta(ruta)
    except ValueError:
        return False
    return ruta_segura.is_file()


__all__ = ["leer", "escribir", "adjuntar", "existe"
    "eliminar",
    "anexar",
    "leer_lineas",]


def eliminar(*args, **kwargs):
    """Delega en ``pcobra.corelibs.archivo.eliminar``."""

    return _archivo.eliminar(*args, **kwargs)


def anexar(*args, **kwargs):
    """Delega en ``pcobra.corelibs.archivo.anexar``."""

    return _archivo.anexar(*args, **kwargs)


def leer_lineas(*args, **kwargs):
    """Delega en ``pcobra.corelibs.archivo.leer_lineas``."""

    return _archivo.leer_lineas(*args, **kwargs)
