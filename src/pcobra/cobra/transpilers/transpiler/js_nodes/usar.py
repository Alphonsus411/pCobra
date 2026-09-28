"""Transpilación JavaScript de la instrucción Cobra ``usar``."""


def visit_usar(self, nodo):
    """Conserva ``usar`` como marcador válido en el backend parcial de JS."""

    modulo = nodo.modulo.translate(
        str.maketrans(
            {"\n": r"\n", "\r": r"\r", "\u2028": r"\u2028", "\u2029": r"\u2029"}
        )
    )
    self.agregar_linea(f"// usar {modulo}")
