def visit_decorador(self, nodo):
    expresion = self.obtener_valor(nodo.expresion)
    self.codigo += f"{self.obtener_indentacion()}@{expresion}\n"
