def visit_retorno(self, nodo):
    valor = self.obtener_valor(nodo.expresion)
    self.codigo += f"{self.obtener_indentacion()}return {valor}\n"
