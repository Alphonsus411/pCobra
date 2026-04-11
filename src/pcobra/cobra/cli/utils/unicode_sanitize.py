from __future__ import annotations


def sanitize_input(text: str) -> str:
    """Sanitiza texto Unicode preservando secuencias válidas y reparando surrogates inválidos.

    Realiza un round-trip UTF-16 con ``surrogatepass`` para mantener pares
    sustitutos válidos (por ejemplo, emoji) y decodifica con ``errors='replace'``
    para convertir surrogates aislados al carácter de reemplazo ``U+FFFD``.

    Ejemplos:
        >>> sanitize_input("Hola, こんにちは, مرحبا 🌍🚀")
        'Hola, こんにちは, مرحبا 🌍🚀'
        >>> sanitize_input("\ud83d")
        '�'
    """
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)

    data = text.encode("utf-16", "surrogatepass")
    return data.decode("utf-16", "replace")
