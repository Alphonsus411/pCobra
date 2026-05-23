def visit_option(self, nodo):
    valor = self.obtener_valor(nodo)
    self.codigo += f"{self.obtener_indentacion()}{valor}\n"
