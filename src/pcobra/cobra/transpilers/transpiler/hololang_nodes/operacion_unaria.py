"""Operaciones unarias en Hololang."""


def visit_operacion_unaria(self, nodo):
    """Transpila una operación unaria como sentencia."""
    self.agregar_linea(f"{self.obtener_valor(nodo)};")
