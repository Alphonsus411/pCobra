"""Soporte de ``yield`` en Hololang."""


def visit_yield(self, nodo):
    """Transpila la expresión ``yield``."""
    valor = self.obtener_valor(nodo.expresion)
    self.agregar_linea(f"yield {valor};")
