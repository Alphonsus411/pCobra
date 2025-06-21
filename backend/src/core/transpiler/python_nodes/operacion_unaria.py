def visit_operacion_unaria(self, nodo):
    self.codigo += self.obtener_valor(nodo)
