"""Operaciones binarias para Hololang."""


def visit_operacion_binaria(self, nodo):
    """Transpila una operación binaria suelta."""
    self.agregar_linea(f"{self.obtener_valor(nodo)};")
