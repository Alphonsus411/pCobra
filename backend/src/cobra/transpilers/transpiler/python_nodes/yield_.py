def visit_yield(self, nodo):
    valor = self.obtener_valor(nodo.expresion)
    self.codigo += f"{self.obtener_indentacion()}yield {valor}\n"
