def visit_yield(self, nodo):
    valor = self.obtener_valor(nodo.expresion)
    self.agregar_linea(f"co_yield {valor};")
