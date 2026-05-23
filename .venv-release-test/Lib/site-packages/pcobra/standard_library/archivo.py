"""Funciones básicas para manipular archivos de texto."""

from __future__ import annotations
from pcobra.corelibs import archivo as _archivo

import os
from pathlib import Path
from typing import Union

PathLike = Union[str, os.PathLike[str]]


def _es_ruta_absoluta_o_sensible_windows(ruta: PathLike) -> bool:
    texto = str(ruta).strip()
    if not texto:
        return False
    if texto.startswith("\\\\"):
        return True
    if len(texto) >= 2 and texto[1] == ":" and texto[0].isalpha():
        return True
    return False


def _resolver_ruta(ruta: PathLike) -> Path:
    """Normaliza ``ruta`` asegurando que permanezca en un directorio seguro."""

    base = Path(os.environ.get("COBRA_IO_BASE_DIR") or Path.cwd()).resolve()
    objetivo = Path(ruta)
    if objetivo.is_absolute() or _es_ruta_absoluta_o_sensible_windows(ruta):
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
        if not isinstance(ruta, str):
            return False
        ruta_segura = _resolver_ruta(ruta)
        return ruta_segura.is_file()
    except Exception:
        # Mantiene el error encapsulado para no exponer tracebacks en REPL.
        return False


PUBLIC_API_ARCHIVO: tuple[str, ...] = (
    "leer",
    "escribir",
    "adjuntar",
    "existe",
    "eliminar",
    "leer_lineas",
    "anexar",
)


def eliminar(*args, **kwargs):
    """Elimina un archivo respetando el sandbox de rutas permitido."""

    return _archivo.eliminar(*args, **kwargs)


def anexar(*args, **kwargs):
    """Alias histórico para agregar contenido al final de un archivo."""

    return _archivo.anexar(*args, **kwargs)


def leer_lineas(*args, **kwargs):
    """Lee un archivo y devuelve sus líneas como lista de texto."""

    return _archivo.leer_lineas(*args, **kwargs)


def _validar_superficie_publica_archivo() -> None:
    if tuple(__all__) != PUBLIC_API_ARCHIVO:
        raise RuntimeError(
            "[STARTUP CONTRACT] standard_library.archivo.__all__ debe exponer solo APIs Cobra-facing."
        )


__all__ = list(PUBLIC_API_ARCHIVO)


_validar_superficie_publica_archivo()
