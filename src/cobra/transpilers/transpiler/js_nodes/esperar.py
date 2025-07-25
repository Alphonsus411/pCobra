def visit_esperar(self, nodo):
    expr = self.obtener_valor(nodo.expresion)
    self.agregar_linea(f"await {expr};")
