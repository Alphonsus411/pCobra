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


def existe(ruta: PathLike) -> bool:
    """Indica si el archivo existe dentro del directorio permitido."""

    try:
        objetivo = Path(ruta)
        if objetivo.is_absolute():
            base = Path(os.environ.get("COBRA_IO_BASE_DIR") or Path.cwd()).resolve()
            destino = objetivo.resolve()
            destino.relative_to(base)
        else:
            destino = _resolver_ruta(objetivo)
    except ValueError:
        return False
    return destino.exists()


def eliminar(ruta: PathLike) -> None:
    """Elimina un archivo dentro del directorio permitido."""

    ruta_segura = _resolver_ruta(ruta) if not Path(ruta).is_absolute() else Path(ruta)
    if ruta_segura.is_absolute():
        base = Path(os.environ.get("COBRA_IO_BASE_DIR") or Path.cwd()).resolve()
        destino = ruta_segura.resolve()
        try:
            destino.relative_to(base)
        except ValueError as exc:
            raise ValueError("La ruta queda fuera del directorio permitido") from exc
        ruta_segura = destino
    else:
        ruta_segura = ruta_segura.resolve()
    try:
        ruta_segura.unlink(missing_ok=True)
    except TypeError:
        # Compatibilidad con versiones de Python anteriores a 3.8.
        if ruta_segura.exists():
            ruta_segura.unlink()
