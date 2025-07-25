def visit_atributo(self, nodo):
    self.agregar_linea(f"ATTR {self.obtener_valor(nodo.objeto)}.{nodo.nombre}")
