"""Biblioteca estándar complementaria para Cobra."""

from __future__ import annotations

from standard_library.archivo import leer, escribir, adjuntar, existe
from standard_library.fecha import hoy, formatear, sumar_dias
from standard_library.lista import (
    cabeza,
    cola,
    longitud,
    combinar,
    mapear_seguro,
    ventanas,
    chunk,
)
from standard_library.logica import conjuncion, disyuncion, negacion
from standard_library.util import es_nulo, es_vacio, rel, repetir
from standard_library.texto import (
    quitar_acentos,
    normalizar_espacios,
    es_palindromo,
    es_anagrama,
)

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
    "mapear_seguro",
    "ventanas",
    "chunk",
    "conjuncion",
    "disyuncion",
    "negacion",
    "es_nulo",
    "es_vacio",
    "rel",
    "repetir",
    "quitar_acentos",
    "normalizar_espacios",
    "es_palindromo",
    "es_anagrama",
]
