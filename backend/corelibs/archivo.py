"""Funciones de manejo de archivos de texto."""

import os


def leer(ruta: str) -> str:
    """Devuelve el contenido de un archivo."""
    with open(ruta, "r", encoding="utf-8") as f:
        return f.read()


def escribir(ruta: str, datos: str) -> None:
    """Escribe *datos* en el archivo indicado."""
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(datos)


def existe(ruta: str) -> bool:
    """Indica si el archivo *ruta* existe."""
    return os.path.exists(ruta)


def eliminar(ruta: str) -> None:
    """Elimina el archivo si existe."""
    if os.path.exists(ruta):
        os.remove(ruta)
