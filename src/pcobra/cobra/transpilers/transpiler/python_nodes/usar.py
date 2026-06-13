def visit_usar(self, nodo):
    """Genera el código para la instrucción ``usar`` usando la API canónica."""

    ind = self.obtener_indentacion()
    kwargs = getattr(self, "contexto_usar_kwargs", lambda: [])()
    args = [repr(nodo.modulo), *(f"{nombre}={valor!r}" for nombre, valor in kwargs)]
    llamada = f"usar_modulo({', '.join(args)})"
    self.codigo += (
        f"{ind}from pcobra.cobra.usar_loader import usar_modulo\n"
        f"{ind}globals().update({llamada})\n"
    )
