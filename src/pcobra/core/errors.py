"""Excepciones comunes del analizador léxico de Cobra."""

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


__all__ = ["LexerError", "InvalidTokenError", "UnclosedStringError"]
