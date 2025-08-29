"""Colección de primitivas nativas disponibles para los programas Cobra."""

from core.nativos.io import leer_archivo, escribir_archivo, obtener_url
from core.nativos.matematicas import sumar, promedio, potencia
from core.nativos.estructuras import Pila, Cola
from ..ctypes_bridge import (
    cargar_biblioteca,
    obtener_funcion,
    cargar_funcion,
)
from ..pybind_bridge import (
    compilar_extension,
    cargar_extension,
    compilar_y_cargar,
)
from ..rust_bridge import (
    compilar_crate,
    cargar_crate,
    compilar_y_cargar_crate,
)

__all__ = [
    "leer_archivo",
    "escribir_archivo",
    "obtener_url",
    "sumar",
    "promedio",
    "potencia",
    "Pila",
    "Cola",
    "cargar_biblioteca",
    "obtener_funcion",
    "cargar_funcion",
    "compilar_extension",
    "cargar_extension",
    "compilar_y_cargar",
    "compilar_crate",
    "cargar_crate",
    "compilar_y_cargar_crate",
]
