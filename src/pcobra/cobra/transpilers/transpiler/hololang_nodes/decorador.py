"""Decoradores en Hololang."""


def visit_decorador(self, nodo):
    """Transpila un decorador antes de funciones o métodos."""
    expresion = self.obtener_valor(nodo.expresion)
    self.agregar_linea(f"@{expresion}")
