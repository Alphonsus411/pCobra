"""Soporte de holobits para Hololang."""


def visit_holobit(self, nodo):
    """Genera la creación de un holobit."""
    valores = ", ".join(self.obtener_valor(v) for v in nodo.valores)
    expresion = f"Holobit::new([{valores}])"
    if getattr(nodo, "nombre", None):
        self.agregar_linea(f"let {nodo.nombre} = {expresion};")
    else:
        self.agregar_linea(f"{expresion};")
