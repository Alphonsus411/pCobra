"""Instanciación de objetos en Hololang."""


def visit_instancia(self, nodo):
    """Transpila la creación de una instancia como sentencia."""
    self.agregar_linea(f"{self.obtener_valor(nodo)};")
