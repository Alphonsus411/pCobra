def visit_llamada_metodo(self, nodo):
    obj = self.obtener_valor(nodo.objeto)
    args = ", ".join(self.obtener_valor(a) for a in nodo.argumentos)
    self.agregar_linea(f"{obj}.{nodo.nombre_metodo}({args});")

