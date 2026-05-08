def visit_option(self, nodo):
    valor = self.obtener_valor(nodo)
    self.agregar_linea(f"{valor};")
