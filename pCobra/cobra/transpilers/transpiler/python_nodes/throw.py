def visit_throw(self, nodo):
    valor = self.obtener_valor(nodo.expresion)
    self.codigo += f"{self.obtener_indentacion()}raise Exception({valor})\n"
