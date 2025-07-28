from difflib import get_close_matches

# Lista de palabras reservadas del lenguaje que no pueden usarse como identificadores
PALABRAS_RESERVADAS = {
    "var",
    "func",
    "rel",
    "si",
    "sino",
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
    "finalmente",
    "desde",
    "como",
    "switch",
    "case",
    "segun",
    "caso",
    "intentar",
    "capturar",
    "lanzar",
}


def sugerir_palabra_clave(palabra: str) -> str | None:
    """Devuelve la palabra clave más parecida si existe una coincidencia."""
    coincidencias = get_close_matches(palabra, PALABRAS_RESERVADAS, n=1, cutoff=0.8)
    return coincidencias[0] if coincidencias else None

