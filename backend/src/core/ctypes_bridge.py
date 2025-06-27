"""Puente sencillo para cargar bibliotecas C usando ``ctypes``."""

from __future__ import annotations

import ctypes
import os
from typing import Any, Iterable


_cache: dict[str, ctypes.CDLL] = {}


def cargar_biblioteca(ruta: str) -> ctypes.CDLL:
    """Carga la biblioteca compartida ubicada en ``ruta``.

    La biblioteca se almacena en una caché interna para evitar cargarse
    varias veces. Se devuelve el objeto :class:`ctypes.CDLL` asociado.
    """
    path = os.path.abspath(ruta)
    if path not in _cache:
        _cache[path] = ctypes.CDLL(path)
    return _cache[path]


def obtener_funcion(lib: ctypes.CDLL, nombre: str,
                    restype: ctypes._CData | None = ctypes.c_int,
                    argtypes: Iterable[ctypes._CData] | None = None) -> Any:
    """Devuelve una función de ``lib`` configurando tipos opcionales."""
    fn = getattr(lib, nombre)
    fn.restype = restype
    if argtypes is not None:
        fn.argtypes = list(argtypes)
    return fn


def cargar_funcion(ruta: str, nombre: str,
                   restype: ctypes._CData | None = ctypes.c_int,
                   argtypes: Iterable[ctypes._CData] | None = None) -> Any:
    """Carga ``ruta`` y devuelve la función indicada."""
    lib = cargar_biblioteca(ruta)
    return obtener_funcion(lib, nombre, restype, argtypes)
