from difflib import get_close_matches
from typing import Union, Literal

# Alias legibles para métodos especiales del ecosistema Python.
ALIAS_METODOS_ESPECIALES = {
    "asignar_atributo": "__setattr__",
    "borrar_atributo": "__delattr__",
    "borrar_item": "__delitem__",
    "booleano": "__bool__",
    "comparar": "__eq__",
    "contener": "__contains__",
    "entrar": "__enter__",
    "entrar_async": "__aenter__",
    "inicializar": "__init__",
    "iterar": "__iter__",
    "llamar": "__call__",
    "longitud": "__len__",
    "obtener_atributo": "__getattr__",
    "obtener_hash": "__hash__",
    "obtener_item": "__getitem__",
    "ordenar": "__lt__",
    "poner_item": "__setitem__",
    "representar": "__repr__",
    "salir": "__exit__",
    "salir_async": "__aexit__",
    "texto": "__str__",
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
        "defer",
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
        "estructura",
        "registro",
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
        "enumeracion",
        "y",
        "o",
        "no",
        "aplazar",
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
