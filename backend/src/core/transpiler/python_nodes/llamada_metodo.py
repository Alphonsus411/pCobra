def visit_llamada_metodo(self, nodo):
    args = ", ".join(self.obtener_valor(a) for a in nodo.argumentos)
    objeto = self.obtener_valor(nodo.objeto)
    self.codigo += f"{objeto}.{nodo.nombre_metodo}({args})\\n"
