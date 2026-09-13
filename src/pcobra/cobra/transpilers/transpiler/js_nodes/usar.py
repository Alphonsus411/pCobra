"""Transpilación JavaScript de la instrucción Cobra ``usar``."""


def visit_usar(self, nodo):
    """Conserva ``usar`` como marcador válido en el backend parcial de JS."""

    self.agregar_linea(f"// usar {nodo.modulo}")
