"""Enumeraciones en Hololang."""


def visit_enum(self, nodo):
    """Transpila la definición de un enum."""
    self.agregar_linea(f"enum {nodo.nombre} {{")
    self.indentacion += 1
    for miembro in nodo.miembros:
        self.agregar_linea(f"{miembro},")
    self.indentacion -= 1
    self.agregar_linea("}")
