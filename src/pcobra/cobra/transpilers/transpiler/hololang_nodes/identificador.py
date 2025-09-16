"""Identificadores en Hololang."""


def visit_identificador(self, nodo):
    """Transpila un identificador como sentencia autónoma."""
    self.agregar_linea(f"{nodo.nombre};")
