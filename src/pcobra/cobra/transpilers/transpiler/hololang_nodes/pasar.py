"""Sentencia ``pasar`` para Hololang."""


def visit_pasar(self, nodo):
    """Transpila una operación nula."""
    self.agregar_linea("// pass")
