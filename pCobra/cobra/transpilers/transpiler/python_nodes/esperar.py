def visit_esperar(self, nodo):
    self.usa_asyncio = True
    expr = self.obtener_valor(nodo.expresion)
    self.codigo += f"{self.obtener_indentacion()}await {expr}\n"
