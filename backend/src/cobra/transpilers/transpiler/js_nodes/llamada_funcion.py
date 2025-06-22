def visit_llamada_funcion(self, nodo):
    """Transpila una llamada a función en JavaScript."""
    parametros = ", ".join(self.obtener_valor(a) for a in nodo.argumentos)
    self.agregar_linea(f"{nodo.nombre}({parametros});")
