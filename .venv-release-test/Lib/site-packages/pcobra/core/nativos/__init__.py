"""Colección de primitivas nativas disponibles para los programas Cobra."""

from .io import leer_archivo, escribir_archivo, obtener_url
from .matematicas import sumar, promedio, potencia
from .estructuras import Pila, Cola
from ..ctypes_bridge import (
    cargar_biblioteca,
    obtener_funcion,
    cargar_funcion,
)
try:
    from ..pybind_bridge import (
        compilar_extension,
        cargar_extension,
        compilar_y_cargar,
    )
except ModuleNotFoundError:  # pragma: no cover - depende de entorno opcional
    def _missing_pybind11(*_args, **_kwargs):
        raise RuntimeError(
            "pybind11 no está disponible. Instala 'pybind11' para usar las primitivas C++"
        )

    compilar_extension = cargar_extension = compilar_y_cargar = _missing_pybind11

try:
    from ..rust_bridge import (
        compilar_crate,
        cargar_crate,
        compilar_y_cargar_crate,
    )
except ModuleNotFoundError:  # pragma: no cover - depende de entorno opcional
    def _missing_rust(*_args, **_kwargs):
        raise RuntimeError(
            "Soporte de Rust no disponible. Instala dependencias opcionales para usarlo"
        )

    compilar_crate = cargar_crate = compilar_y_cargar_crate = _missing_rust

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
