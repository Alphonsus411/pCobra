"""Diccionarios en Hololang."""


def visit_diccionario(self, nodo):
    """Transpila un literal de diccionario como instrucción."""
    self.agregar_linea(f"{self.obtener_valor(nodo)};")
