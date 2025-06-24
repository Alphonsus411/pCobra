def visit_llamada_funcion(self, nodo):
    args = ", ".join(self.obtener_valor(a) for a in nodo.argumentos)
    self.agregar_linea(f"{nodo.nombre}({args});")
