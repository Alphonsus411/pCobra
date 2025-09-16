"""Creación de hilos en Hololang."""


def visit_hilo(self, nodo):
    """Transpila la creación de un hilo."""
    llamada = self.obtener_valor(nodo.llamada)
    self.agregar_linea(f"spawn {llamada};")
