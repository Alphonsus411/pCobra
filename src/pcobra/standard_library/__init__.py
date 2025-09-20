"""Biblioteca estándar complementaria para Cobra.

Este paquete expone utilidades enfocadas en manipular colecciones, texto,
fechas y datos tabulares mediante envoltorios amigables. Cada función
re-exportada incluye anotaciones de tipo para favorecer el autocompletado y la
documentación en español, con notas sobre compatibilidad funcional con
ecosistemas como R o Julia cuando aplica.

Ejemplos rápidos::

    from standard_library import (
        preguntar_texto,
        preguntar_opcion,
        preguntar_entero,
    )

    nombre = preguntar_texto("¿Cómo te llamas?", por_defecto="Ada")
    color = preguntar_opcion("Color favorito", ["azul", "verde", "rojo"], por_defecto="azul")
    edad = preguntar_entero("Edad", minimo=0)

    print(f"{nombre} prefiere el {color} y tiene {edad} años")
"""

from __future__ import annotations

import asyncio

from typing import Any, Awaitable, Callable, Coroutine, Iterable, Mapping, Sequence, TypeVar

from standard_library.archivo import leer, escribir, adjuntar, existe
from standard_library.datos import (
    agrupar_y_resumir,
    a_listas,
    de_listas,
    describir,
    filtrar,
    desplegar_tabla,
    mutar_columna,
    pivotar_ancho,
    pivotar_largo,
    separar_columna,
    unir_columnas,
    leer_csv,
    leer_excel,
    leer_feather,
    leer_json,
    leer_parquet,
    escribir_csv,
    escribir_excel,
    escribir_feather,
    escribir_json,
    escribir_parquet,
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
    preguntar_confirmacion,
    preguntar_entero,
    preguntar_opcion,
    preguntar_texto,
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
    condicional,
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
    es_titulo,
    es_digito,
    es_espacio,
    prefijo_comun,
    sufijo_comun,
    indentar_texto,
    desindentar_texto,
    envolver_texto,
    acortar_texto,
    intercambiar_mayusculas,
    expandir_tabulaciones,
)
from standard_library.numero import (
    es_finito,
    es_infinito,
    es_nan,
    copiar_signo,
    signo,
    limitar,
    interpolar,
    envolver_modular,
)
from standard_library.util import es_nulo, es_vacio, rel, repetir
from standard_library.asincrono import grupo_tareas, proteger_tarea, ejecutar_en_hilo

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
    "condicional",
    "xor",
    "nand",
    "nor",
    "implica",
    "equivale",
    "xor_multiple",
    "todas",
    "alguna",
    "es_finito",
    "es_infinito",
    "signo",
    "limitar",
    "es_nan",
    "copiar_signo",
    "interpolar",
    "envolver_modular",
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
    "es_titulo",
    "es_digito",
    "es_espacio",
    "prefijo_comun",
    "sufijo_comun",
    "indentar_texto",
    "desindentar_texto",
    "envolver_texto",
    "acortar_texto",
    "intercambiar_mayusculas",
    "expandir_tabulaciones",
    "leer_csv",
    "leer_json",
    "leer_excel",
    "leer_parquet",
    "leer_feather",
    "describir",
    "seleccionar_columnas",
    "filtrar",
    "mutar_columna",
    "separar_columna",
    "unir_columnas",
    "pivotar_ancho",
    "pivotar_largo",
    "desplegar_tabla",
    "agrupar_y_resumir",
    "a_listas",
    "de_listas",
    "escribir_csv",
    "escribir_json",
    "escribir_excel",
    "escribir_parquet",
    "escribir_feather",
    "mostrar_tabla",
    "preguntar_confirmacion",
    "preguntar_texto",
    "preguntar_opcion",
    "preguntar_entero",
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
    "grupo_tareas",
    "proteger_tarea",
    "ejecutar_en_hilo",
]


# Se exponen las firmas para mejorar el autocompletado en editores compatibles.
leer_csv: Callable[..., list[dict[str, Any]]]
leer_json: Callable[..., list[dict[str, Any]]]
leer_excel: Callable[..., list[dict[str, Any]]]
leer_parquet: Callable[..., list[dict[str, Any]]]
leer_feather: Callable[..., list[dict[str, Any]]]
describir: Callable[[Iterable[dict[str, Any]] | Mapping[str, Sequence[Any]]], dict[str, Any]]
seleccionar_columnas: Callable[[Iterable[dict[str, Any]] | Mapping[str, Sequence[Any]], Sequence[str]], list[dict[str, Any]]]
filtrar: Callable[[Iterable[dict[str, Any]] | Mapping[str, Sequence[Any]], Callable[[dict[str, Any]], bool]], list[dict[str, Any]]]
mutar_columna: Callable[[Iterable[dict[str, Any]] | Mapping[str, Sequence[Any]], str, Callable[[dict[str, Any]], Any]], list[dict[str, Any]]]
pivotar_ancho: Callable[..., list[dict[str, Any]]]
pivotar_largo: Callable[..., list[dict[str, Any]]]
desplegar_tabla: Callable[..., list[dict[str, Any]]]
agrupar_y_resumir: Callable[[Iterable[dict[str, Any]] | Mapping[str, Sequence[Any]], Sequence[str], Mapping[str, Any]], list[dict[str, Any]]]
a_listas: Callable[[Iterable[dict[str, Any]] | Mapping[str, Sequence[Any]]], dict[str, list[Any]]]
de_listas: Callable[[Mapping[str, Sequence[Any]]], list[dict[str, Any]]]
escribir_csv: Callable[..., None]
escribir_json: Callable[..., None]
escribir_excel: Callable[..., None]
escribir_parquet: Callable[..., None]
escribir_feather: Callable[..., None]
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

T_co = TypeVar("T_co")
proteger_tarea: Callable[[Awaitable[T_co] | Coroutine[Any, Any, T_co]], asyncio.Future[T_co]]
ejecutar_en_hilo: Callable[..., Awaitable[Any]]
