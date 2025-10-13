"""Utilidades para compilar y cargar bibliotecas Rust."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Iterable, Any

from .ctypes_bridge import cargar_biblioteca, obtener_funcion


def compilar_crate(ruta: str, release: bool = True, timeout: int = 300) -> str:
    """Compila el crate Rust ubicado en ``ruta`` y devuelve la ruta de la
    biblioteca generada.

    Se ejecuta ``cbindgen`` para generar los encabezados C y ``cargo`` para
    construir la biblioteca como ``cdylib``. Si ``release`` es ``False`` se
    compilar\u00e1 en modo debug. El par\u00e1metro ``timeout`` establece el tiempo
    m\u00e1ximo en segundos para cada comando externo.
    """
    path = Path(ruta).resolve()

    if shutil.which("cbindgen") is None:
        raise RuntimeError(
            "La herramienta 'cbindgen' no est\xc3\xa1 instalada o no se encuentra en PATH"
        )

    if shutil.which("cargo") is None:
        raise RuntimeError(
            "La herramienta 'cargo' no est\xc3\xa1 instalada o no se encuentra en PATH"
        )

    try:
        subprocess.run(
            [
                "cbindgen",
                str(path),
                "-o",
                str(path / "bindings.h"),
            ],
            check=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            "Tiempo de espera excedido al ejecutar cbindgen"
        ) from exc

    cmd = [
        "cargo",
        "build",
        "--manifest-path",
        str(path / "Cargo.toml"),
    ]
    if release:
        cmd.append("--release")
    try:
        subprocess.run(cmd, check=True, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            "Tiempo de espera excedido al ejecutar cargo"
        ) from exc

    target = path / "target" / ("release" if release else "debug")
    base = f"lib{path.name}"
    for ext in (".so", ".dylib", ".dll"):
        lib = target / f"{base}{ext}"
        if lib.exists():
            return str(lib)
    raise FileNotFoundError("Biblioteca generada no encontrada")


def cargar_crate(ruta: str, release: bool = True, timeout: int = 300) -> Any:
    """Compila y carga el crate localizado en ``ruta``.

    El par\u00e1metro ``timeout`` establece el tiempo m\u00e1ximo en segundos para
    cada comando externo.
    """
    lib_path = compilar_crate(ruta, release, timeout)
    return cargar_biblioteca(lib_path)


def compilar_y_cargar_crate(ruta: str, nombre: str, *,
                            release: bool = True,
                            timeout: int = 300,
                            restype: Any | None = None,
                            argtypes: Iterable[Any] | None = None) -> Any:
    """Compila ``ruta`` y devuelve la funci\u00f3n ``nombre`` lista para usar.

    ``timeout`` establece el tiempo m\u00e1ximo en segundos para cada comando
    externo.
    """
    lib = cargar_crate(ruta, release, timeout)
    return obtener_funcion(lib, nombre, restype, argtypes)
