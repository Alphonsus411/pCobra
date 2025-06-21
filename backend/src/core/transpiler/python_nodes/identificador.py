def visit_identificador(self, nodo):
    self.codigo += self.obtener_valor(nodo)
