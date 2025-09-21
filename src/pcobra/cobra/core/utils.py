from difflib import get_close_matches
from typing import Union, Literal

# Alias legibles para métodos especiales del ecosistema Python.
ALIAS_METODOS_ESPECIALES = {
    "inicializar": "__init__",
    "representar": "__repr__",
    "iterar": "__iter__",
    "longitud": "__len__",
    "contener": "__contains__",
    "comparar": "__eq__",
    "ordenar": "__lt__",
    "entrar": "__enter__",
    "salir": "__exit__",
}

# Umbral de similitud para las coincidencias
UMBRAL_COINCIDENCIA = 0.8

# Lista de palabras reservadas del lenguaje que no pueden usarse como identificadores
PALABRAS_RESERVADAS = frozenset(
    {
        "var",
        "func",
        "si",
        "sino",
        "sino si",
        "elseif",
        "garantia",
        "guard",
        "mientras",
        "para",
        "import",
        "try",
        "catch",
        "throw",
        "hilo",
        "retorno",
        "fin",
        "in",
        "holobit",
        "imprimir",
        "proyectar",
        "transformar",
        "graficar",
        "usar",
        "macro",
        "clase",
        "interface",
        "metodo",
        "atributo",
        "decorador",
        "yield",
        "romper",
        "continuar",
        "pasar",
        "afirmar",
        "eliminar",
        "global",
        "nolocal",
        "lambda",
        "asincronico",
        "esperar",
        "con",
        "with",
        "finalmente",
        "desde",
        "como",
        "as",
        "switch",
        "case",
        "segun",
        "caso",
        "intentar",
        "capturar",
        "lanzar",
        "option",
        "enum",
        "y",
        "o",
        "no",
    }
)


def sugerir_palabra_clave(palabra: str) -> Union[str, Literal[None]]:
    """Devuelve la palabra clave más parecida si existe una coincidencia.

    Args:
        palabra: La palabra para la cual se busca una coincidencia entre las palabras reservadas.
            Debe ser una cadena no vacía.

    Returns:
        str: La palabra reservada más similar si se encuentra una coincidencia con
            similitud mayor a UMBRAL_COINCIDENCIA.
        None: Si no se encuentra ninguna coincidencia o si la entrada es inválida.

    Examples:
        >>> sugerir_palabra_clave("imprim")
        'imprimir'
        >>> sugerir_palabra_clave("whil")
        'mientras'
        >>> sugerir_palabra_clave("")
        None
    """
    if not palabra or not isinstance(palabra, str):
        return None

    try:
        coincidencias = get_close_matches(
            palabra, PALABRAS_RESERVADAS, n=1, cutoff=UMBRAL_COINCIDENCIA
        )
        return coincidencias[0] if coincidencias else None
    except (IndexError, TypeError):
        return None
