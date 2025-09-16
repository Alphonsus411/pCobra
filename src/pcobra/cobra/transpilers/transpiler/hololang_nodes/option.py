"""Opciones en Hololang."""


def visit_option(self, nodo):
    """Transpila un valor opcional."""
    valor = self.obtener_valor(nodo)
    self.agregar_linea(f"{valor};")
