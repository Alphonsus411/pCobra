"""Funciones de texto de alto nivel basadas en ``pcobra.corelibs.texto``.

Ejemplo rápido::

    import standard_library.texto as texto

    texto.quitar_prefijo("🧪Prueba", "🧪")  # -> "Prueba"
    texto.centrar_texto("cobra", 10, "-")    # -> "---cobra--"
    texto.dividir_lineas("uno\r\ndos\n", conservar_delimitadores=True)
    # -> ["uno\r\n", "dos\n"]
    texto.subcadena_despues("ruta/archivo.txt", "/")  # -> "archivo.txt"
"""

from __future__ import annotations

from typing import Any, TypeVar, overload

import unicodedata
from pcobra.corelibs import (
    centrar_texto as _centrar_texto,
    contar_subcadena as _contar_subcadena,
    dividir,
    dividir_derecha as _dividir_derecha,
    dividir_lineas as _dividir_lineas,
    indentar_texto as _indentar_texto,
    desindentar_texto as _desindentar_texto,
    envolver_texto as _envolver_texto,
    acortar_texto as _acortar_texto,
    invertir,
    minusculas,
    minusculas_casefold as _minusculas_casefold,
    normalizar_unicode,
    quitar_espacios,
    quitar_prefijo as _quitar_prefijo,
    quitar_sufijo as _quitar_sufijo,
    particionar_derecha as _particionar_derecha,
    particionar_texto as _particionar,
    rellenar_ceros as _rellenar_ceros,
    subcadena_antes as _subcadena_antes,
    subcadena_despues as _subcadena_despues,
    subcadena_antes_ultima as _subcadena_antes_ultima,
    subcadena_despues_ultima as _subcadena_despues_ultima,
    unir,
    es_alfabetico as _es_alfabetico,
    es_alfa_numerico as _es_alfa_numerico,
    es_decimal as _es_decimal,
    es_numerico as _es_numerico,
    es_identificador as _es_identificador,
    es_imprimible as _es_imprimible,
    es_ascii as _es_ascii,
    es_mayusculas as _es_mayusculas,
    es_minusculas as _es_minusculas,
    es_espacio as _es_espacio,
)

_T = TypeVar("_T")
_SIN_VALOR = object()

__all__ = [
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
    "quitar_prefijo",
    "quitar_sufijo",
    "dividir_lineas",
    "dividir_derecha",
    "subcadena_antes",
    "subcadena_despues",
    "subcadena_antes_ultima",
    "subcadena_despues_ultima",
    "contar_subcadena",
    "centrar_texto",
    "rellenar_ceros",
    "minusculas_casefold",
    "particionar",
    "particionar_derecha",
    "indentar_texto",
    "desindentar_texto",
    "envolver_texto",
    "acortar_texto",
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


def es_alfabetico(texto: str) -> bool:
    """Equivale a :meth:`str.isalpha` en Python y acepta letras Unicode."""

    return _es_alfabetico(texto)


def es_alfa_numerico(texto: str) -> bool:
    """Alias en español de :meth:`str.isalnum` para letras o dígitos Unicode."""

    return _es_alfa_numerico(texto)


def es_decimal(texto: str) -> bool:
    """Replica :meth:`str.isdecimal` comprobando solo dígitos decimales."""

    return _es_decimal(texto)


def es_numerico(texto: str) -> bool:
    """Se alinea con :meth:`str.isnumeric` y acepta números Unicode amplios."""

    return _es_numerico(texto)


def es_identificador(texto: str) -> bool:
    """Aplica las reglas de :meth:`str.isidentifier` para nombres válidos en Python."""

    return _es_identificador(texto)


def es_imprimible(texto: str) -> bool:
    """Devuelve lo mismo que :meth:`str.isprintable` sobre caracteres visibles."""

    return _es_imprimible(texto)


def es_ascii(texto: str) -> bool:
    """Equivalente a :meth:`str.isascii` para cadenas limitadas al ASCII."""

    return _es_ascii(texto)


def es_mayusculas(texto: str) -> bool:
    """Imita :meth:`str.isupper` asegurando al menos una letra en mayúsculas."""

    return _es_mayusculas(texto)


def es_minusculas(texto: str) -> bool:
    """Funciona como :meth:`str.islower` validando letras en minúscula."""

    return _es_minusculas(texto)


def es_espacio(texto: str) -> bool:
    """Corresponde a :meth:`str.isspace` para secuencias de espacios Unicode."""

    return _es_espacio(texto)


def indentar_texto(
    texto: str,
    prefijo: str,
    *,
    solo_lineas_no_vacias: bool = False,
) -> str:
    """Añade un prefijo por línea, igual que :func:`textwrap.indent` en Python."""

    return _indentar_texto(texto, prefijo, solo_lineas_no_vacias=solo_lineas_no_vacias)


def desindentar_texto(texto: str) -> str:
    """Elimina la sangría común como hace :func:`textwrap.dedent` en Python."""

    return _desindentar_texto(texto)


def envolver_texto(
    texto: str,
    ancho: int = 70,
    *,
    indentacion_inicial: str = "",
    indentacion_subsecuente: str = "",
    como_texto: bool = False,
) -> list[str] | str:
    """Ajusta párrafos usando :func:`textwrap.wrap` o ``fill`` según ``como_texto``."""

    return _envolver_texto(
        texto,
        ancho,
        indentacion_inicial=indentacion_inicial,
        indentacion_subsecuente=indentacion_subsecuente,
        como_texto=como_texto,
    )


def acortar_texto(
    texto: str,
    ancho: int,
    *,
    marcador: str = " [...]",
) -> str:
    """Resume frases como :func:`textwrap.shorten`, añadiendo ``marcador`` si recorta."""

    return _acortar_texto(texto, ancho, marcador=marcador)


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


def dividir_derecha(
    texto: str, separador: str | None = None, maximo: int | None = None
) -> list[str]:
    """Divide ``texto`` desde la derecha respetando las reglas de ``str.rsplit``.

    Ejemplo::

        dividir_derecha("uno-dos-tres", "-", 1)  # -> ["uno-dos", "tres"]
    """

    return _dividir_derecha(texto, separador, maximo)


@overload
def subcadena_antes(texto: str, separador: str) -> str:
    ...


@overload
def subcadena_antes(texto: str, separador: str, por_defecto: _T) -> str | _T:
    ...


def subcadena_antes(texto: str, separador: str, por_defecto: Any = _SIN_VALOR) -> Any:
    """Devuelve lo que antecede al primer ``separador``.

    Equivalente a ``substringBefore`` de Kotlin y admite un ``por_defecto`` para
    los casos en los que el separador no aparezca. Los separadores vacíos se
    consideran presentes al inicio de la cadena.
    """

    if por_defecto is _SIN_VALOR:
        return _subcadena_antes(texto, separador)
    return _subcadena_antes(texto, separador, por_defecto)


@overload
def subcadena_despues(texto: str, separador: str) -> str:
    ...


@overload
def subcadena_despues(texto: str, separador: str, por_defecto: _T) -> str | _T:
    ...


def subcadena_despues(texto: str, separador: str, por_defecto: Any = _SIN_VALOR) -> Any:
    """Obtiene el texto que sigue al primer ``separador``.

    Mantiene la semántica de ``substringAfter`` de Kotlin, devolviendo ``texto``
    completo salvo que se indique ``por_defecto`` cuando no hay coincidencias.
    """

    if por_defecto is _SIN_VALOR:
        return _subcadena_despues(texto, separador)
    return _subcadena_despues(texto, separador, por_defecto)


@overload
def subcadena_antes_ultima(texto: str, separador: str) -> str:
    ...


@overload
def subcadena_antes_ultima(
    texto: str, separador: str, por_defecto: _T
) -> str | _T:
    ...


def subcadena_antes_ultima(
    texto: str, separador: str, por_defecto: Any = _SIN_VALOR
) -> Any:
    """Devuelve lo que hay antes de la última coincidencia de ``separador``.

    Equivale a ``substringBeforeLast`` en Kotlin y permite definir ``por_defecto``
    para ausencias del separador. Los delimitadores vacíos se consideran
    presentes al final de la cadena.
    """

    if por_defecto is _SIN_VALOR:
        return _subcadena_antes_ultima(texto, separador)
    return _subcadena_antes_ultima(texto, separador, por_defecto)


@overload
def subcadena_despues_ultima(texto: str, separador: str) -> str:
    ...


@overload
def subcadena_despues_ultima(
    texto: str, separador: str, por_defecto: _T
) -> str | _T:
    ...


def subcadena_despues_ultima(
    texto: str, separador: str, por_defecto: Any = _SIN_VALOR
) -> Any:
    """Retorna lo posterior a la última aparición de ``separador``.

    Replica la semántica de ``substringAfterLast`` en Kotlin permitiendo ajustar
    ``por_defecto`` cuando no hay coincidencias.
    """

    if por_defecto is _SIN_VALOR:
        return _subcadena_despues_ultima(texto, separador)
    return _subcadena_despues_ultima(texto, separador, por_defecto)


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


def particionar(texto: str, separador: str) -> tuple[str, str, str]:
    """Particiona ``texto`` alrededor del primer ``separador`` encontrado."""

    return _particionar(texto, separador)


def particionar_derecha(texto: str, separador: str) -> tuple[str, str, str]:
    """Particiona ``texto`` tomando la última coincidencia de ``separador``."""

    return _particionar_derecha(texto, separador)
