def visit_identificador(self, nodo):
    self.agregar_linea(self.obtener_valor(nodo))
