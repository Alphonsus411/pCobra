"""Resolución interna de rutas confinadas para las corelibs de E/S.

Si ``COBRA_IO_BASE_DIR`` no está configurada, el sandbox usa un directorio
temporal exclusivo del proceso, creado con permisos privados por
``tempfile.mkdtemp``. Este módulo es deliberadamente interno y no forma parte
de las superficies públicas de :mod:`pcobra.corelibs`.
"""

from __future__ import annotations

import os
import tempfile
import threading
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Final

_VARIABLE_RAIZ: Final = "COBRA_IO_BASE_DIR"
_raiz_privada: Path | None = None
_bloqueo_raiz = threading.Lock()


def _obtener_raiz() -> Path:
    """Devuelve la raíz configurada o crea una privada para este proceso."""

    configurada = os.environ.get(_VARIABLE_RAIZ)
    if configurada:
        raiz = Path(configurada).expanduser().resolve(strict=True)
        if not raiz.is_dir():
            raise NotADirectoryError(f"La raíz del sandbox no es un directorio: {raiz}")
        return raiz

    global _raiz_privada
    if _raiz_privada is None:
        with _bloqueo_raiz:
            if _raiz_privada is None:
                _raiz_privada = Path(tempfile.mkdtemp(prefix="pcobra-io-"))
    return _raiz_privada.resolve(strict=True)


def _normalizar_ruta_usuario(ruta: str | os.PathLike[str]) -> Path:
    texto = os.fspath(ruta)
    if not isinstance(texto, str):
        raise TypeError("La ruta debe ser texto")
    if not texto or "\x00" in texto:
        raise ValueError("La ruta no es válida")

    # Se comprueban ambas sintaxis antes de adaptar separadores al anfitrión.
    if PurePosixPath(texto).is_absolute() or PureWindowsPath(texto).is_absolute():
        raise ValueError("Las rutas absolutas no están permitidas")
    normalizada = Path(texto.replace("\\", "/"))
    if ".." in normalizada.parts:
        raise ValueError("La ruta no puede contener '..'")
    return normalizada


def _comprobar_confinamiento(ruta: Path, raiz: Path) -> Path:
    try:
        ruta.relative_to(raiz)
    except ValueError as exc:
        raise ValueError("La ruta queda fuera del directorio permitido") from exc
    return ruta


def resolver_ruta_existente(ruta: str | os.PathLike[str]) -> Path:
    """Resuelve una ruta relativa existente y confinada dentro del sandbox."""

    raiz = _obtener_raiz()
    objetivo = (raiz / _normalizar_ruta_usuario(ruta)).resolve(strict=True)
    return _comprobar_confinamiento(objetivo, raiz)


def resolver_destino_nuevo(ruta: str | os.PathLike[str]) -> Path:
    """Resuelve un destino nuevo validando primero su confinamiento.

    Los directorios intermedios pueden no existir todavía. Se resuelve el
    ancestro existente más próximo para detectar enlaces simbólicos salientes
    sin crear nada antes de completar la validación.
    """

    raiz = _obtener_raiz()
    destino = raiz / _normalizar_ruta_usuario(ruta)
    if destino.is_symlink():
        raise ValueError("El destino no puede ser un enlace simbólico")
    ancestro = destino.parent
    partes_pendientes: list[str] = []
    while not ancestro.exists():
        partes_pendientes.append(ancestro.name)
        ancestro = ancestro.parent
    ancestro_real = ancestro.resolve(strict=True)
    _comprobar_confinamiento(ancestro_real, raiz)
    padre_validado = ancestro_real.joinpath(*reversed(partes_pendientes))
    _comprobar_confinamiento(padre_validado, raiz)
    destino_validado = padre_validado / destino.name
    _comprobar_confinamiento(destino_validado.resolve(strict=False), raiz)
    return destino_validado
