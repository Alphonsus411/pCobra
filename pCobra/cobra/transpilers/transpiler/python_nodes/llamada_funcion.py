def visit_llamada_funcion(self, nodo):
    argumentos = ", ".join(self.obtener_valor(arg) for arg in nodo.argumentos)
    self.codigo += f"{nodo.nombre}({argumentos})\n"
