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


def dividir_derecha(
    texto: str, separador: str | None = None, maximo: int | None = None
) -> list[str]:
    """Divide ``texto`` desde la derecha usando ``str.rsplit``.

    Cuando ``separador`` es ``None`` se emplea cualquier secuencia de espacios en blanco
    como delimitador y se ignoran resultados vacíos consecutivos, igual que hace
    :meth:`str.rsplit`. ``maximo`` limita el número de divisiones que se realizarán.

    Args:
        texto: Cadena a fragmentar.
        separador: Cadena que actuará como separador. Si es ``None`` se consideran
            espacios en blanco.
        maximo: Número máximo de divisiones a efectuar. ``None`` o valores negativos
            se interpretan como "sin límite".

    Returns:
        Lista de subcadenas obtenida desde la derecha hacia la izquierda.

    Raises:
        ValueError: Si ``separador`` es una cadena vacía.
    """

    if separador == "":
        raise ValueError("separador no puede ser una cadena vacía")

    if maximo is None or maximo < 0:
        maxsplit = -1
    else:
        maxsplit = maximo
    return texto.rsplit(separador, maxsplit)


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


def quitar_prefijo(texto: str, prefijo: str) -> str:
    """Emula ``str.removeprefix`` de Python, ``strings.TrimPrefix`` de Go y el patrón ``startsWith``/``slice`` de JavaScript."""

    if prefijo and texto.startswith(prefijo):
        return texto[len(prefijo) :]
    return texto


def quitar_sufijo(texto: str, sufijo: str) -> str:
    """Replica ``str.removesuffix`` de Python, ``strings.TrimSuffix`` en Go y el recorte con ``endsWith``/``slice`` en JavaScript."""

    if sufijo and texto.endswith(sufijo):
        return texto[: -len(sufijo)]
    return texto


def rellenar_izquierda(texto: str, ancho: int, relleno: str = " ") -> str:
    """Rellena ``texto`` por la izquierda hasta alcanzar ``ancho`` caracteres."""

    if ancho <= len(texto):
        return texto
    if not relleno:
        raise ValueError("relleno no puede ser una cadena vacía")
    faltan = ancho - len(texto)
    repetidos = (relleno * ((faltan // len(relleno)) + 1))[:faltan]
    return repetidos + texto


def particionar(texto: str, separador: str) -> tuple[str, str, str]:
    """Particiona ``texto`` alrededor de ``separador`` usando ``str.partition``.

    Args:
        texto: Cadena completa que se desea segmentar.
        separador: Delimitador exacto a localizar dentro de ``texto``.

    Returns:
        Una tupla ``(antes, separador, despues)``. Si el separador no aparece,
        ``antes`` será ``texto`` completo y los otros dos elementos serán cadenas
        vacías.

    Raises:
        TypeError: Si ``separador`` no es una cadena.
        ValueError: Si ``separador`` es una cadena vacía.
    """

    if not isinstance(separador, str):
        raise TypeError("separador debe ser una cadena")
    if separador == "":
        raise ValueError("separador no puede ser una cadena vacía")
    return texto.partition(separador)


def particionar_derecha(texto: str, separador: str) -> tuple[str, str, str]:
    """Particiona ``texto`` desde la derecha utilizando ``str.rpartition``.

    Args:
        texto: Cadena de origen.
        separador: Delimitador que se intentará localizar.

    Returns:
        Una tupla ``(antes, separador, despues)`` donde ``antes`` contiene todo lo que
        aparece a la izquierda de la última ocurrencia de ``separador``. Si el
        separador no está presente se devuelve ``("", "", texto)``.

    Raises:
        TypeError: Si ``separador`` no es una cadena.
        ValueError: Si ``separador`` es una cadena vacía.
    """

    if not isinstance(separador, str):
        raise TypeError("separador debe ser una cadena")
    if separador == "":
        raise ValueError("separador no puede ser una cadena vacía")
    return texto.rpartition(separador)


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


def dividir_lineas(texto: str, conservar_delimitadores: bool = False) -> list[str]:
    """Hace eco de ``str.splitlines`` (Python), ``bufio.Scanner`` (Go) y ``String.prototype.split`` (JS)."""

    return texto.splitlines(keepends=conservar_delimitadores)


def contar_subcadena(
    texto: str,
    subcadena: str,
    inicio: int | None = None,
    fin: int | None = None,
) -> int:
    """Imita ``str.count`` (Python), ``strings.Count`` (Go) y ``String.prototype.split`` para conteos en JS."""

    if inicio is None and fin is None:
        return texto.count(subcadena)
    if inicio is None:
        return texto.count(subcadena, 0, fin)
    if fin is None:
        return texto.count(subcadena, inicio)
    return texto.count(subcadena, inicio, fin)


def centrar_texto(texto: str, ancho: int, relleno: str = " ") -> str:
    """Se alinea con ``str.center`` (Python), ``strings.Repeat`` en Go y ``padStart``/``padEnd`` en JS."""

    return texto.center(ancho, relleno)


def rellenar_ceros(texto: str, ancho: int) -> str:
    """Equivale a ``str.zfill`` (Python), ``fmt.Sprintf`` en Go y ``padStart`` con ``'0'`` en JS."""

    return texto.zfill(ancho)


def minusculas_casefold(texto: str) -> str:
    """Aplica ``str.casefold`` (Python), ``cases.Fold`` del paquete ``x/text`` en Go y ``toLocaleLowerCase`` estricto en JS."""

    return texto.casefold()
