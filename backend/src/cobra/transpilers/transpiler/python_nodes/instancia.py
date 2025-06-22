def visit_instancia(self, nodo):
    self.codigo += f"{self.obtener_valor(nodo)}\n"
