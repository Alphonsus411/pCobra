def visit_llamada_metodo(self, nodo):
    args = ", ".join(self.obtener_valor(a) for a in nodo.argumentos)
    obj = self.obtener_valor(nodo.objeto)
    self.agregar_linea(f"{obj}.{nodo.nombre_metodo}({args});")
