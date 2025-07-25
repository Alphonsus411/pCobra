"""Funciones utilitarias para manipular cadenas de texto."""


def mayusculas(texto: str) -> str:
    """Devuelve *texto* en mayúsculas."""
    return texto.upper()


def minusculas(texto: str) -> str:
    """Devuelve *texto* en minúsculas."""
    return texto.lower()


def invertir(texto: str) -> str:
    """Invierte el contenido de *texto*."""
    return texto[::-1]


def concatenar(*cadenas: str) -> str:
    """Concatena las cadenas proporcionadas."""
    return "".join(cadenas)
