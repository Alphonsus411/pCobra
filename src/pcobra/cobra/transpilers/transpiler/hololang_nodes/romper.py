"""Sentencias ``break`` en Hololang."""


def visit_romper(self, nodo):
    """Transpila un ``break``."""
    self.agregar_linea("break;")
