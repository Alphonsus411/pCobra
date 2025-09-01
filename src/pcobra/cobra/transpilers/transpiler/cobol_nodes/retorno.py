"""Nodo COBOL para manejar sentencias de retorno."""


def visit_retorno(self, nodo):
    """Muestra el valor de retorno usando DISPLAY."""
    valor = self.obtener_valor(getattr(nodo, "expresion", None))
    self.agregar_linea(f"DISPLAY {valor}")

