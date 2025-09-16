"""Acceso a atributos en Hololang."""


def visit_atributo(self, nodo):
    """Transpila el acceso a un atributo como sentencia autónoma."""
    self.agregar_linea(f"{self.obtener_valor(nodo)};")
