"""Llamadas a métodos en Hololang."""


def visit_llamada_metodo(self, nodo):
    """Transpila la invocación de un método."""
    args = ", ".join(self.obtener_valor(arg) for arg in nodo.argumentos)
    objeto = self.obtener_valor(nodo.objeto)
    self.agregar_linea(f"{objeto}.{nodo.nombre_metodo}({args});")
