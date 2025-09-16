"""Llamadas a función en Hololang."""


def visit_llamada_funcion(self, nodo):
    """Transpila la llamada a una función."""
    args = ", ".join(self.obtener_valor(arg) for arg in nodo.argumentos)
    self.agregar_linea(f"{nodo.nombre}({args});")
