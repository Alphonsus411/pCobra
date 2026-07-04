"""Utilidades para crear y limpiar rutas temporales en Cobra."""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional, Union

PathLike = Union[str, os.PathLike[str]]

__all__ = ["archivo_temporal", "directorio_temporal", "limpiar"]


def _validar_texto_opcional(valor: Optional[str], nombre_argumento: str) -> Optional[str]:
    if valor is None:
        return None
    if not isinstance(valor, str):
        raise TypeError(f"{nombre_argumento} debe ser texto o None")
    return valor


def _validar_ruta(ruta: PathLike) -> PathLike:
    if not isinstance(ruta, (str, os.PathLike)):
        raise TypeError("ruta debe ser una ruta de texto o compatible con os.PathLike")
    texto = os.fspath(ruta)
    if not isinstance(texto, str):
        raise TypeError("ruta debe representar una ruta de texto")
    if texto == "":
        raise ValueError("ruta no puede estar vacía")
    return ruta


def archivo_temporal(
    *, prefijo: Optional[str] = None, sufijo: Optional[str] = None, texto: bool = True
) -> str:
    """Crea un archivo temporal vacío y devuelve su ruta como texto.

    El descriptor creado por :func:`tempfile.mkstemp` se cierra inmediatamente para
    evitar fugas de recursos. ``texto`` selecciona si el archivo se abre en modo de
    texto o binario durante la creación, siguiendo la semántica de ``mkstemp``.
    """

    prefijo_validado = _validar_texto_opcional(prefijo, "prefijo")
    sufijo_validado = _validar_texto_opcional(sufijo, "sufijo")
    if not isinstance(texto, bool):
        raise TypeError("texto debe ser booleano")

    descriptor, ruta = tempfile.mkstemp(
        prefix=prefijo_validado, suffix=sufijo_validado, text=texto
    )
    os.close(descriptor)
    return str(Path(ruta))


def directorio_temporal(*, prefijo: Optional[str] = None) -> str:
    """Crea un directorio temporal y devuelve su ruta como texto."""

    prefijo_validado = _validar_texto_opcional(prefijo, "prefijo")
    return str(Path(tempfile.mkdtemp(prefix=prefijo_validado)))


def limpiar(ruta: PathLike) -> bool:
    """Elimina un archivo o directorio temporal de forma segura.

    Devuelve ``True`` cuando elimina una ruta existente. Si ``ruta`` no existe,
    devuelve ``False`` de manera determinista y no crea errores.
    """

    ruta_validada = _validar_ruta(ruta)
    objetivo = Path(ruta_validada)

    if not objetivo.exists():
        return False
    try:
        if objetivo.is_dir() and not objetivo.is_symlink():
            shutil.rmtree(objetivo)
        else:
            objetivo.unlink()
    except FileNotFoundError:
        return False
    return True
