def visit_throw(self, nodo):
    val = self.obtener_valor(nodo.expresion)
    self.agregar_linea(f"THROW {val}")
