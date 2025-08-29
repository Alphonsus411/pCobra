"""Funciones básicas para manipular archivos de texto."""

from __future__ import annotations

import os


def leer(ruta: str) -> str:
    """Devuelve el contenido de un archivo."""
    with open(ruta, "r", encoding="utf-8") as f:
        return f.read()


def escribir(ruta: str, datos: str) -> None:
    """Sobrescribe el archivo indicado con ``datos``."""
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(datos)


def adjuntar(ruta: str, datos: str) -> None:
    """Agrega ``datos`` al final del archivo."""
    with open(ruta, "a", encoding="utf-8") as f:
        f.write(datos)


def existe(ruta: str) -> bool:
    """Indica si el archivo existe."""
    return os.path.isfile(ruta)

