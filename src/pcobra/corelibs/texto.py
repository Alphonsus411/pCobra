"""Funciones utilitarias para manipular cadenas de texto."""

from __future__ import annotations

from collections.abc import Iterable
import unicodedata


def mayusculas(texto: str) -> str:
    """Devuelve ``texto`` en mayúsculas utilizando las reglas Unicode."""

    return texto.upper()


def minusculas(texto: str) -> str:
    """Devuelve ``texto`` en minúsculas utilizando las reglas Unicode."""

    return texto.lower()


def capitalizar(texto: str) -> str:
    """Devuelve ``texto`` con la primera letra en mayúscula y el resto en minúscula."""

    return texto.capitalize()


def titulo(texto: str) -> str:
    """Convierte ``texto`` a formato título respetando separadores comunes."""

    return texto.title()


def invertir(texto: str) -> str:
    """Invierte el contenido de ``texto`` carácter por carácter."""

    return texto[::-1]


def concatenar(*cadenas: str) -> str:
    """Concatena las cadenas proporcionadas sin separador adicional."""

    return "".join(cadenas)


def quitar_espacios(
    texto: str,
    modo: str = "ambos",
    caracteres: str | None = None,
) -> str:
    """Elimina espacios en blanco o caracteres específicos de ``texto``.

    Args:
        texto: Cadena original.
        modo: Indica qué lados limpiar: ``"ambos"`` (por defecto), ``"izquierda"``
            o ``"derecha"``.
        caracteres: Conjunto de caracteres a eliminar. Si es ``None`` se usan los
            espacios en blanco definidos por Unicode.

    Raises:
        ValueError: Si ``modo`` no es uno de los valores permitidos.

    """

    if modo not in {"ambos", "izquierda", "derecha"}:
        raise ValueError("modo debe ser 'ambos', 'izquierda' o 'derecha'")

    if modo == "ambos":
        return texto.strip(caracteres) if caracteres is not None else texto.strip()
    if modo == "izquierda":
        return texto.lstrip(caracteres) if caracteres is not None else texto.lstrip()
    return texto.rstrip(caracteres) if caracteres is not None else texto.rstrip()


def dividir(texto: str, separador: str | None = None, maximo: int | None = None) -> list[str]:
    """Divide ``texto`` en una lista de subcadenas.

    El comportamiento replica a :meth:`str.split`. Cuando ``separador`` es ``None`` se
    agrupan los bloques separados por espacios en blanco (según Unicode) y se ignoran
    bloques vacíos consecutivos. ``maximo`` limita el número de divisiones; si es
    ``None`` o un número negativo se interpretará como sin límite.
    """

    if maximo is None or maximo < 0:
        maxsplit = -1
    else:
        maxsplit = maximo
    return texto.split(separador, maxsplit)


def unir(separador: str, piezas: Iterable[str]) -> str:
    """Une ``piezas`` empleando ``separador`` como delimitador."""

    return separador.join(str(parte) for parte in piezas)


def reemplazar(
    texto: str,
    antiguo: str,
    nuevo: str,
    conteo: int | None = None,
) -> str:
    """Reemplaza apariciones de ``antiguo`` por ``nuevo`` dentro de ``texto``.

    Args:
        texto: Cadena original.
        antiguo: Subcadena a sustituir.
        nuevo: Texto que reemplazará a ``antiguo``.
        conteo: Número máximo de reemplazos. ``None`` o valores negativos significan
            "sin límite".
    """

    if conteo is None or conteo < 0:
        return texto.replace(antiguo, nuevo)
    return texto.replace(antiguo, nuevo, conteo)


def empieza_con(texto: str, prefijos: str | tuple[str, ...]) -> bool:
    """Indica si ``texto`` comienza con alguno de los ``prefijos`` indicados."""

    return texto.startswith(prefijos)


def termina_con(texto: str, sufijos: str | tuple[str, ...]) -> bool:
    """Indica si ``texto`` termina con alguno de los ``sufijos`` indicados."""

    return texto.endswith(sufijos)


def incluye(texto: str, subcadena: str) -> bool:
    """Comprueba si ``subcadena`` está contenida dentro de ``texto``."""

    return subcadena in texto


def rellenar_izquierda(texto: str, ancho: int, relleno: str = " ") -> str:
    """Rellena ``texto`` por la izquierda hasta alcanzar ``ancho`` caracteres."""

    if ancho <= len(texto):
        return texto
    if not relleno:
        raise ValueError("relleno no puede ser una cadena vacía")
    faltan = ancho - len(texto)
    repetidos = (relleno * ((faltan // len(relleno)) + 1))[:faltan]
    return repetidos + texto


def rellenar_derecha(texto: str, ancho: int, relleno: str = " ") -> str:
    """Rellena ``texto`` por la derecha hasta alcanzar ``ancho`` caracteres."""

    if ancho <= len(texto):
        return texto
    if not relleno:
        raise ValueError("relleno no puede ser una cadena vacía")
    faltan = ancho - len(texto)
    repetidos = (relleno * ((faltan // len(relleno)) + 1))[:faltan]
    return texto + repetidos


def normalizar_unicode(texto: str, forma: str = "NFC") -> str:
    """Normaliza ``texto`` a la forma Unicode especificada.

    Args:
        texto: Cadena a normalizar.
        forma: Debe ser una de ``"NFC"``, ``"NFD"``, ``"NFKC"`` o ``"NFKD"``.

    Raises:
        ValueError: Si ``forma`` no es válida.
    """

    formas_permitidas = {"NFC", "NFD", "NFKC", "NFKD"}
    if forma not in formas_permitidas:
        raise ValueError(f"forma debe ser una de {sorted(formas_permitidas)}")
    return unicodedata.normalize(forma, texto)
