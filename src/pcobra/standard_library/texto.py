"""Funciones de texto de alto nivel basadas en ``pcobra.corelibs.texto``."""

from __future__ import annotations

import unicodedata
from pcobra.corelibs import (
    dividir,
    invertir,
    minusculas,
    normalizar_unicode,
    quitar_espacios,
    unir,
)

__all__ = ["quitar_acentos", "normalizar_espacios", "es_palindromo", "es_anagrama"]


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
