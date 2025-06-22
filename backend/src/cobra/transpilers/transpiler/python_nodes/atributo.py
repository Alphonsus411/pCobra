def visit_atributo(self, nodo):
    self.codigo += f"{self.obtener_valor(nodo)}\n"
