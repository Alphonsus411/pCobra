"""Funciones de texto de alto nivel basadas en ``pcobra.corelibs.texto``.

Ejemplo rápido::

    import standard_library.texto as texto

    texto.quitar_prefijo("🧪Prueba", "🧪")  # -> "Prueba"
    texto.centrar_texto("cobra", 10, "-")    # -> "---cobra--"
    texto.dividir_lineas("uno\r\ndos\n", conservar_delimitadores=True)
    # -> ["uno\r\n", "dos\n"]
"""

from __future__ import annotations

import unicodedata
from pcobra.corelibs import (
    centrar_texto as _centrar_texto,
    contar_subcadena as _contar_subcadena,
    dividir,
    dividir_lineas as _dividir_lineas,
    invertir,
    minusculas,
    minusculas_casefold as _minusculas_casefold,
    normalizar_unicode,
    quitar_espacios,
    quitar_prefijo as _quitar_prefijo,
    quitar_sufijo as _quitar_sufijo,
    rellenar_ceros as _rellenar_ceros,
    unir,
)

__all__ = [
    "quitar_acentos",
    "normalizar_espacios",
    "es_palindromo",
    "es_anagrama",
    "quitar_prefijo",
    "quitar_sufijo",
    "dividir_lineas",
    "contar_subcadena",
    "centrar_texto",
    "rellenar_ceros",
    "minusculas_casefold",
]


def quitar_acentos(texto: str) -> str:
    """Elimina diacríticos de ``texto`` conservando los caracteres base."""

    descompuesto = unicodedata.normalize("NFD", texto)
    sin_marcas = "".join(
        caracter
        for caracter in descompuesto
        if unicodedata.category(caracter) != "Mn"
    )
    return unicodedata.normalize("NFC", sin_marcas)


def normalizar_espacios(texto: str) -> str:
    """Colapsa grupos de espacios en blanco y elimina los bordes vacíos."""

    partes = dividir(texto)
    return unir(" ", partes) if partes else ""


def es_palindromo(
    texto: str,
    *,
    ignorar_espacios: bool = True,
    ignorar_tildes: bool = True,
    ignorar_mayusculas: bool = True,
) -> bool:
    """Indica si ``texto`` es un palíndromo bajo las reglas solicitadas."""

    procesado = texto
    if ignorar_espacios:
        procesado = "".join(dividir(procesado))
    else:
        procesado = quitar_espacios(procesado, modo="ambos")
    if ignorar_tildes:
        procesado = quitar_acentos(procesado)
    if ignorar_mayusculas:
        procesado = minusculas(procesado)
    return procesado == invertir(procesado)


def es_anagrama(texto: str, otro: str, *, ignorar_espacios: bool = True) -> bool:
    """Comprueba si dos cadenas son anagramas considerando acentos y espacios."""

    def preparar(valor: str) -> str:
        resultado = quitar_acentos(valor)
        if ignorar_espacios:
            resultado = "".join(dividir(resultado))
        resultado = minusculas(resultado)
        return normalizar_unicode("".join(sorted(resultado)), "NFC")

    return preparar(texto) == preparar(otro)


def quitar_prefijo(texto: str, prefijo: str) -> str:
    """Elimina ``prefijo`` cuando ``texto`` lo contiene al inicio.

    Ejemplo::

        quitar_prefijo("foobar", "foo")  # -> "bar"
    """

    return _quitar_prefijo(texto, prefijo)


def quitar_sufijo(texto: str, sufijo: str) -> str:
    """Recorta ``sufijo`` si ``texto`` termina con él.

    Ejemplo::

        quitar_sufijo("archivo.tmp", ".tmp")  # -> "archivo"
    """

    return _quitar_sufijo(texto, sufijo)


def dividir_lineas(texto: str, conservar_delimitadores: bool = False) -> list[str]:
    """Divide ``texto`` por saltos de línea sin perder combinaciones ``\r\n``.

    Args:
        texto: Contenido multilinea a segmentar.
        conservar_delimitadores: Cuando es ``True`` preserva los separadores.
    """

    return _dividir_lineas(texto, conservar_delimitadores)


def contar_subcadena(
    texto: str,
    subcadena: str,
    inicio: int | None = None,
    fin: int | None = None,
) -> int:
    """Cuenta apariciones de ``subcadena`` respetando ``inicio`` y ``fin``.

    Ejemplo::

        contar_subcadena("banana", "na")  # -> 2
    """

    return _contar_subcadena(texto, subcadena, inicio, fin)


def centrar_texto(texto: str, ancho: int, relleno: str = " ") -> str:
    """Centra ``texto`` a ``ancho`` caracteres usando ``relleno``.

    Ejemplo::

        centrar_texto("cobra", 9, "*")  # -> "**cobra**"
    """

    return _centrar_texto(texto, ancho, relleno)


def rellenar_ceros(texto: str, ancho: int) -> str:
    """Completa ``texto`` con ceros a la izquierda preservando signos."""

    return _rellenar_ceros(texto, ancho)


def minusculas_casefold(texto: str) -> str:
    """Devuelve ``texto`` en minúsculas intensivas según Unicode (casefold)."""

    return _minusculas_casefold(texto)
