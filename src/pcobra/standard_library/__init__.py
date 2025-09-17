"""Biblioteca estándar complementaria para Cobra.

Este paquete expone utilidades enfocadas en manipular colecciones, texto,
fechas y ahora datos tabulares mediante envoltorios amigables. Cada función
re-exportada incluye anotaciones de tipo para favorecer el autocompletado y la
documentación en español para facilitar su consulta.
"""

from __future__ import annotations

from typing import Any, Callable, Iterable, Mapping, Sequence

from standard_library.archivo import leer, escribir, adjuntar, existe
from standard_library.datos import (
    agrupar_y_resumir,
    a_listas,
    de_listas,
    describir,
    filtrar,
    leer_csv,
    leer_json,
    seleccionar_columnas,
)
from standard_library.fecha import hoy, formatear, sumar_dias
from standard_library.lista import (
    cabeza,
    chunk,
    cola,
    combinar,
    longitud,
    mapear_seguro,
    ventanas,
)
from standard_library.logica import conjuncion, disyuncion, negacion
from standard_library.texto import (
    es_anagrama,
    es_palindromo,
    normalizar_espacios,
    quitar_acentos,
)
from standard_library.util import es_nulo, es_vacio, rel, repetir

__all__: list[str] = [
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
    "leer_csv",
    "leer_json",
    "describir",
    "seleccionar_columnas",
    "filtrar",
    "agrupar_y_resumir",
    "a_listas",
    "de_listas",
]


# Se exponen las firmas para mejorar el autocompletado en editores compatibles.
leer_csv: Callable[..., list[dict[str, Any]]]
leer_json: Callable[..., list[dict[str, Any]]]
describir: Callable[[Iterable[dict[str, Any]] | Mapping[str, Sequence[Any]]], dict[str, Any]]
seleccionar_columnas: Callable[[Iterable[dict[str, Any]] | Mapping[str, Sequence[Any]], Sequence[str]], list[dict[str, Any]]]
filtrar: Callable[[Iterable[dict[str, Any]] | Mapping[str, Sequence[Any]], Callable[[dict[str, Any]], bool]], list[dict[str, Any]]]
agrupar_y_resumir: Callable[[Iterable[dict[str, Any]] | Mapping[str, Sequence[Any]], Sequence[str], Mapping[str, Any]], list[dict[str, Any]]]
a_listas: Callable[[Iterable[dict[str, Any]] | Mapping[str, Sequence[Any]]], dict[str, list[Any]]]
de_listas: Callable[[Mapping[str, Sequence[Any]]], list[dict[str, Any]]]
