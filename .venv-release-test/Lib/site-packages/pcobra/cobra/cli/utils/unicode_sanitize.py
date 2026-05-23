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


def sanitize_source_for_tokenizer(text: str) -> str:
    """Sanitiza código fuente para tokenización sin mutar Lexer/Parser.

    - Repara surrogates inválidos mediante ``sanitize_input``.
    - Dentro de literales de cadena simples/dobles, convierte caracteres
      no-ASCII a secuencias de escape Unicode (``\\u``/``\\U``), para que el
      ``Lexer`` actual los reconstruya correctamente al decodificar
      ``unicode_escape``.
    """
    source = sanitize_input(text)
    out: list[str] = []
    quote: str | None = None
    escaped = False

    for ch in source:
        if quote is None:
            out.append(ch)
            if ch in {"'", '"'}:
                quote = ch
                escaped = False
            continue

        if escaped:
            out.append(ch)
            escaped = False
            continue

        if ch == "\\":
            out.append(ch)
            escaped = True
            continue

        if ch == quote:
            out.append(ch)
            quote = None
            continue

        if ord(ch) > 127:
            out.append(ch.encode("unicode_escape").decode("ascii"))
            continue

        out.append(ch)

    return "".join(out)
