from src.cobra.usar_loader import obtener_modulo


def visit_usar(self, nodo):
    """Genera el código para la instrucción ``usar``."""

    ind = self.obtener_indentacion()
    self.codigo += (
        f"{ind}from src.cobra.usar_loader import obtener_modulo\n"
        f"{ind}{nodo.modulo} = obtener_modulo('{nodo.modulo}')\n"
    )
