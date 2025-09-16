"""Operación de proyección para Hololang."""


def visit_proyectar(self, nodo):
    """Transpila la llamada a ``proyectar`` sobre un holobit."""
    hb = self.obtener_valor(nodo.holobit)
    modo = self.obtener_valor(nodo.modo)
    self.agregar_linea(f"project({hb}, {modo});")
