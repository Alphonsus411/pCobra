"""Valores literales en Hololang."""


def visit_valor(self, nodo):
    """Escribe un valor literal como sentencia independiente."""
    self.agregar_linea(f"{self.obtener_valor(nodo)};")
