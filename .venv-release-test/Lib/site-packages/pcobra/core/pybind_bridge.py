"""Utilidades para compilar y cargar extensiones C++ con ``pybind11``."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import os
import tempfile
import shutil
from types import ModuleType
from typing import Dict, Iterable, Optional

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import Distribution

_cache: Dict[str, ModuleType] = {}

# Prefijos permitidos para cargar extensiones
_ALLOWED_PREFIXES: list[str] = [
    os.path.abspath(p)
    for p in os.environ.get(
        "COBRA_ALLOWED_EXT_PATHS", "/usr/lib:/usr/local/lib"
    ).split(os.pathsep)
    if p
]


def _es_ruta_permitida(ruta: str) -> bool:
    path = os.path.abspath(ruta)
    for pref in _ALLOWED_PREFIXES:
        pref = os.path.abspath(pref)
        try:
            if os.path.commonpath([pref, path]) == pref:
                return True
        except ValueError:
            continue
    return False


def compilar_extension(
    nombre: str,
    codigo: str,
    directorio: str | None = None,
    extra_cflags: Optional[Iterable[str]] = None,
    conservar: bool = False,
) -> str:
    """Compila ``codigo`` como una extensión Python usando ``pybind11``.

    Se devuelve la ruta absoluta del archivo generado (.so, .pyd, etc.).
    Si ``conservar`` es ``False`` y no se proporciona ``directorio``, el
    contenido temporal generado será eliminado al finalizar.
    """
    cleanup = directorio is None
    if directorio is None:
        directorio = tempfile.mkdtemp()
    cpp = os.path.join(directorio, f"{nombre}.cpp")
    with open(cpp, "w", encoding="utf-8") as fh:
        fh.write(codigo)

    ext = Pybind11Extension(
        nombre, [cpp], extra_compile_args=list(extra_cflags or [])
    )
    dist = Distribution({"name": nombre, "ext_modules": [ext]})
    cmd = build_ext(dist)
    cmd.build_lib = directorio
    cmd.build_temp = os.path.join(directorio, "temp")
    cmd.finalize_options()
    try:
        cmd.run()
        return os.path.join(directorio, cmd.get_ext_filename(nombre))
    finally:
        if cleanup and not conservar:
            shutil.rmtree(directorio, ignore_errors=True)


def cargar_extension(ruta: str) -> ModuleType:
    """Carga la extensión ubicada en ``ruta`` y la almacena en caché."""
    path = os.path.abspath(ruta)
    if not _es_ruta_permitida(path):
        raise ValueError(f"Ruta no permitida: {ruta}")
    if path not in _cache:
        nombre = os.path.splitext(os.path.basename(path))[0]
        loader = importlib.machinery.ExtensionFileLoader(nombre, path)
        spec = importlib.util.spec_from_loader(loader.name, loader)
        if spec is None:
            raise ImportError(f"No se pudo obtener un spec para {path}")
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)
        _cache[path] = module
    return _cache[path]


def compilar_y_cargar(
    nombre: str,
    codigo: str,
    directorio: str | None = None,
    extra_cflags: Optional[Iterable[str]] = None,
    conservar: bool = False,
) -> ModuleType:
    """Compila ``codigo`` y devuelve el módulo resultante."""
    propio = directorio is None
    path = compilar_extension(
        nombre, codigo, directorio, extra_cflags, conservar=True
    )
    mod = cargar_extension(path)
    if propio and not conservar:
        shutil.rmtree(os.path.dirname(path), ignore_errors=True)
    return mod
