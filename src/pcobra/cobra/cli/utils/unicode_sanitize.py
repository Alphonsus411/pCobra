from __future__ import annotations


def sanitize_input(text: str) -> str:
    """Sanitiza texto Unicode preservando pares válidos y reparando surrogates inválidos.

    Esta función hace un round-trip por UTF-16 usando ``surrogatepass`` para
    conservar secuencias Unicode válidas (por ejemplo, emoji correctos) y luego
    decodifica con ``errors='replace'`` para convertir surrogates rotos en el
    carácter de reemplazo ``U+FFFD``.

    Ejemplos:
        >>> sanitize_input("áéíóú 🚀")
        'áéíóú 🚀'
        >>> sanitize_input("\ud83d")
        '�'
    """
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)

    data = text.encode("utf-16", "surrogatepass")
    return data.decode("utf-16", "replace")
