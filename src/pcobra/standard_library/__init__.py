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
    desplegar_tabla,
    leer_csv,
    leer_excel,
    leer_json,
    escribir_excel,
    seleccionar_columnas,
)
from standard_library.fecha import hoy, formatear, sumar_dias
from standard_library.interfaz import (
    barra_progreso,
    grupo_consola,
    imprimir_aviso,
    iniciar_gui,
    iniciar_gui_idle,
    limpiar_consola,
    mostrar_columnas,
    mostrar_markdown,
    mostrar_json,
    mostrar_panel,
    mostrar_tabla,
)
from standard_library.lista import (
    cabeza,
    chunk,
    cola,
    combinar,
    longitud,
    mapear_seguro,
    ventanas,
)
from standard_library.logica import (
    es_verdadero,
    es_falso,
    conjuncion,
    disyuncion,
    negacion,
    xor,
    nand,
    nor,
    implica,
    equivale,
    xor_multiple,
    todas,
    alguna,
)
from standard_library.texto import (
    es_anagrama,
    es_palindromo,
    normalizar_espacios,
    quitar_acentos,
    es_alfabetico,
    es_alfa_numerico,
    es_decimal,
    es_numerico,
    es_identificador,
    es_imprimible,
    es_ascii,
    es_mayusculas,
    es_minusculas,
    es_espacio,
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
    "es_verdadero",
    "es_falso",
    "conjuncion",
    "disyuncion",
    "negacion",
    "xor",
    "nand",
    "nor",
    "implica",
    "equivale",
    "xor_multiple",
    "todas",
    "alguna",
    "es_nulo",
    "es_vacio",
    "rel",
    "repetir",
    "quitar_acentos",
    "normalizar_espacios",
    "es_palindromo",
    "es_anagrama",
    "es_alfabetico",
    "es_alfa_numerico",
    "es_decimal",
    "es_numerico",
    "es_identificador",
    "es_imprimible",
    "es_ascii",
    "es_mayusculas",
    "es_minusculas",
    "es_espacio",
    "leer_csv",
    "leer_json",
    "leer_excel",
    "describir",
    "seleccionar_columnas",
    "filtrar",
    "desplegar_tabla",
    "agrupar_y_resumir",
    "a_listas",
    "de_listas",
    "escribir_excel",
    "mostrar_tabla",
    "mostrar_columnas",
    "mostrar_panel",
    "mostrar_markdown",
    "mostrar_json",
    "grupo_consola",
    "barra_progreso",
    "limpiar_consola",
    "imprimir_aviso",
    "iniciar_gui",
    "iniciar_gui_idle",
]


# Se exponen las firmas para mejorar el autocompletado en editores compatibles.
leer_csv: Callable[..., list[dict[str, Any]]]
leer_json: Callable[..., list[dict[str, Any]]]
leer_excel: Callable[..., list[dict[str, Any]]]
describir: Callable[[Iterable[dict[str, Any]] | Mapping[str, Sequence[Any]]], dict[str, Any]]
seleccionar_columnas: Callable[[Iterable[dict[str, Any]] | Mapping[str, Sequence[Any]], Sequence[str]], list[dict[str, Any]]]
filtrar: Callable[[Iterable[dict[str, Any]] | Mapping[str, Sequence[Any]], Callable[[dict[str, Any]], bool]], list[dict[str, Any]]]
desplegar_tabla: Callable[..., list[dict[str, Any]]]
agrupar_y_resumir: Callable[[Iterable[dict[str, Any]] | Mapping[str, Sequence[Any]], Sequence[str], Mapping[str, Any]], list[dict[str, Any]]]
a_listas: Callable[[Iterable[dict[str, Any]] | Mapping[str, Sequence[Any]]], dict[str, list[Any]]]
de_listas: Callable[[Mapping[str, Sequence[Any]]], list[dict[str, Any]]]
escribir_excel: Callable[..., None]
mostrar_tabla: Callable[..., Any]
mostrar_columnas: Callable[..., Any]
mostrar_panel: Callable[..., Any]
mostrar_markdown: Callable[..., Any]
mostrar_json: Callable[..., Any]
grupo_consola: Callable[..., Any]
barra_progreso: Callable[..., Any]
limpiar_consola: Callable[..., None]
imprimir_aviso: Callable[..., None]
iniciar_gui: Callable[..., None]
iniciar_gui_idle: Callable[..., None]
