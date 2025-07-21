"""Biblioteca estándar complementaria para Cobra."""

from __future__ import annotations

from standard_library.archivo import leer, escribir, adjuntar, existe
from standard_library.fecha import hoy, formatear, sumar_dias
from standard_library.lista import cabeza, cola, longitud, combinar
from standard_library.logica import conjuncion, disyuncion, negacion
from standard_library.util import es_nulo, es_vacio, repetir

__all__ = [
    "leer",
    "escribir",
    "adjuntar",
    "existe",
    "hoy",
    "formatear",
    "sumar_dias",
    "cabeza",
    "cola",
    "longitud",
    "combinar",
    "conjuncion",
    "disyuncion",
    "negacion",
    "es_nulo",
    "es_vacio",
    "repetir",
]
