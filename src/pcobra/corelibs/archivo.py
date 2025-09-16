"""Funciones de manejo de archivos de texto."""

import os
from pathlib import Path
from typing import Union

PathLike = Union[str, os.PathLike[str]]


def _resolver_ruta(ruta: PathLike) -> Path:
    """Normaliza ``ruta`` dentro de un directorio permitido.

    Se utiliza ``COBRA_IO_BASE_DIR`` como directorio base si está definido;
    en caso contrario se emplea el directorio de trabajo actual. Si la ruta
    resultante se sale de este directorio controlado, se genera un
    ``ValueError``.
    """

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
    """Escribe ``datos`` en un archivo dentro del directorio permitido.

    La ruta debe permanecer dentro de ``COBRA_IO_BASE_DIR`` (si existe) o del
    directorio de trabajo actual. Se lanza ``ValueError`` si la ruta no es
    válida.
    """

    ruta_segura = _resolver_ruta(ruta)
    with ruta_segura.open("w", encoding="utf-8") as f:
        f.write(datos)


def existe(ruta: str) -> bool:
    """Indica si el archivo *ruta* existe."""
    return os.path.exists(ruta)


def eliminar(ruta: str) -> None:
    """Elimina el archivo si existe."""
    if os.path.exists(ruta):
        os.remove(ruta)
