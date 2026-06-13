def visit_usar(self, nodo):
    """Genera el código para la instrucción ``usar`` usando la API canónica."""

    ind = self.obtener_indentacion()
    self.codigo += (
        f"{ind}from pcobra.cobra.usar_loader import usar_modulo\n"
        f"{ind}globals().update(usar_modulo('{nodo.modulo}'))\n"
    )
