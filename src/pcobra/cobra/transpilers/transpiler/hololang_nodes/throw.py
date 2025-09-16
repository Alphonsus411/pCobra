"""Lanzamiento de excepciones para Hololang."""


def visit_throw(self, nodo):
    """Transpila ``throw``."""
    expr = self.obtener_valor(nodo.expresion)
    self.agregar_linea(f"throw {expr};")
