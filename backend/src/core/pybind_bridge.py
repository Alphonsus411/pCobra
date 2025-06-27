"""Utilidades para compilar y cargar extensiones C++ con ``pybind11``."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import os
import tempfile
from types import ModuleType
from typing import Dict, Iterable, Optional

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import Distribution


_cache: Dict[str, ModuleType] = {}


def compilar_extension(nombre: str, codigo: str, directorio: str | None = None,
                       extra_cflags: Optional[Iterable[str]] = None) -> str:
    """Compila ``codigo`` como una extensi\u00f3n Python usando ``pybind11``.

    Se devuelve la ruta absoluta del archivo generado (.so, .pyd, etc.).
    """
    if directorio is None:
        directorio = tempfile.mkdtemp()
    cpp = os.path.join(directorio, f"{nombre}.cpp")
    with open(cpp, "w", encoding="utf-8") as fh:
        fh.write(codigo)

    ext = Pybind11Extension(nombre, [cpp],
                             extra_compile_args=list(extra_cflags or []))
    dist = Distribution({"name": nombre, "ext_modules": [ext]})
    cmd = build_ext(dist)
    cmd.build_lib = directorio
    cmd.build_temp = os.path.join(directorio, "temp")
    cmd.finalize_options()
    cmd.run()

    return os.path.join(directorio, cmd.get_ext_filename(nombre))


def cargar_extension(ruta: str) -> ModuleType:
    """Carga la extensi\u00f3n ubicada en ``ruta`` y la almacena en cach\u00e9."""
    path = os.path.abspath(ruta)
    if path not in _cache:
        nombre = os.path.splitext(os.path.basename(path))[0]
        loader = importlib.machinery.ExtensionFileLoader(nombre, path)
        spec = importlib.util.spec_from_loader(loader.name, loader)
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)
        _cache[path] = module
    return _cache[path]


def compilar_y_cargar(nombre: str, codigo: str, directorio: str | None = None,
                      extra_cflags: Optional[Iterable[str]] = None) -> ModuleType:
    """Compila ``codigo`` y devuelve el m\u00f3dulo resultante."""
    path = compilar_extension(nombre, codigo, directorio, extra_cflags)
    return cargar_extension(path)
