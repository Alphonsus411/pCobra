"""Lectura de archivos de configuración TOML e INI para las corelibs."""

from __future__ import annotations

import configparser
import importlib
import importlib.util
import os
from pathlib import Path
from types import ModuleType
from typing import Any

__all__ = [
    "leer_toml",
    "leer_ini",
    "toml_disponible",
    "leer_configuracion",
]

_TOML_NO_SOPORTADO = "TOML no está soportado en este entorno de Python: falta tomllib"
_FORMATOS_SOPORTADOS = ".toml, .ini, .cfg"
PathLike = str | os.PathLike[str]


def toml_disponible() -> bool:
    """Indica si el intérprete actual incluye soporte estándar para TOML."""

    return importlib.util.find_spec("tomllib") is not None


def leer_toml(ruta: PathLike) -> dict[str, Any]:
    """Lee un archivo TOML desde ``ruta`` usando ``tomllib`` de la biblioteca estándar."""

    ruta_configuracion = _validar_archivo_existente(ruta)
    tomllib = _cargar_tomllib()

    with ruta_configuracion.open("rb") as archivo:
        return tomllib.load(archivo)


def leer_ini(ruta: PathLike) -> dict[str, dict[str, str]]:
    """Lee un archivo INI/CFG y devuelve sus secciones como diccionarios."""

    ruta_configuracion = _validar_archivo_existente(ruta)
    parser = configparser.ConfigParser()

    with ruta_configuracion.open("r", encoding="utf-8") as archivo:
        parser.read_file(archivo, source=str(ruta_configuracion))

    configuracion: dict[str, dict[str, str]] = {}
    if parser.defaults():
        configuracion[parser.default_section] = dict(parser.defaults())

    for seccion in parser.sections():
        configuracion[seccion] = dict(parser[seccion])

    return configuracion


def leer_configuracion(ruta: PathLike) -> dict[str, Any] | dict[str, dict[str, str]]:
    """Lee ``ruta`` eligiendo el parser por extensión: ``.toml``, ``.ini`` o ``.cfg``."""

    ruta_configuracion = _validar_archivo_existente(ruta)
    extension = ruta_configuracion.suffix.lower()

    if extension == ".toml":
        return leer_toml(ruta_configuracion)
    if extension in {".ini", ".cfg"}:
        return leer_ini(ruta_configuracion)

    raise ValueError(
        f"Formato de configuración no soportado para '{ruta_configuracion}'; "
        f"extensiones soportadas: {_FORMATOS_SOPORTADOS}"
    )


def _validar_archivo_existente(ruta: PathLike) -> Path:
    if not isinstance(ruta, (str, os.PathLike)):
        raise TypeError("ruta debe ser una ruta de texto o compatible con os.PathLike")
    texto = os.fspath(ruta)
    if not isinstance(texto, str):
        raise TypeError("ruta debe representar una ruta de texto")
    if texto == "":
        raise ValueError("ruta no puede estar vacía")
    ruta_configuracion = Path(texto)
    if not ruta_configuracion.is_file():
        raise FileNotFoundError(
            f"Archivo de configuración no encontrado: {ruta_configuracion}"
        )
    return ruta_configuracion


def _cargar_tomllib() -> ModuleType:
    if not toml_disponible():
        raise RuntimeError(_TOML_NO_SOPORTADO)

    return importlib.import_module("tomllib")
