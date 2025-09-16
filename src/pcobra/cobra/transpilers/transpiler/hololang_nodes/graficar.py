"""Visualización de holobits en Hololang."""


def visit_graficar(self, nodo):
    """Transpila la llamada ``graficar``."""
    hb = self.obtener_valor(nodo.holobit)
    self.agregar_linea(f"render({hb});")
