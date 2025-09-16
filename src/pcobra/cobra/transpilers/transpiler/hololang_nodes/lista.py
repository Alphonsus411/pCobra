"""Listas en Hololang."""


def visit_lista(self, nodo):
    """Transpila un literal de lista como instrucción independiente."""
    self.agregar_linea(f"{self.obtener_valor(nodo)};")
