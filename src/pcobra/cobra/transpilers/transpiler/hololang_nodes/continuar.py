"""Sentencias ``continue`` en Hololang."""


def visit_continuar(self, nodo):
    """Transpila un ``continue``."""
    self.agregar_linea("continue;")
