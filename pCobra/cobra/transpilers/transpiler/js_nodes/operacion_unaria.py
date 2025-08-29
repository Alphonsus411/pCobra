def visit_operacion_unaria(self, nodo):
    self.agregar_linea(self.obtener_valor(nodo))
