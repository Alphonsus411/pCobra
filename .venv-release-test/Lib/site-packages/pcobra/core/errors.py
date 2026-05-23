"""Excepciones comunes del núcleo de Cobra."""

class LexerError(Exception):
    """Excepción base para errores del analizador léxico."""

    def __init__(self, mensaje: str, linea: int, columna: int) -> None:
        super().__init__(mensaje)
        self.linea = linea
        self.columna = columna


class InvalidTokenError(LexerError):
    """Excepción para símbolos no reconocidos."""

    pass


class UnclosedStringError(LexerError):
    """Excepción para cadenas sin cerrar."""

    pass


class CondicionNoBooleanaError(Exception):
    """Error semántico cuando una condición de control no es booleana."""

    MENSAJE_POR_DEFECTO = "La condición debe ser booleana"

    def __init__(self, mensaje: str = MENSAJE_POR_DEFECTO) -> None:
        super().__init__(mensaje)


__all__ = [
    "LexerError",
    "InvalidTokenError",
    "UnclosedStringError",
    "CondicionNoBooleanaError",
]
