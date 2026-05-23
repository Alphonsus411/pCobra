def visit_throw(self, nodo):
    valor = self.obtener_valor(nodo.expresion)
    self.agregar_linea(f"throw {valor};")
