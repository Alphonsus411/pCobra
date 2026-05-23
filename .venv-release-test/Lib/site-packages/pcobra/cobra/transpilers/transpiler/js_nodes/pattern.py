def visit_pattern(self, nodo):
    patron = self.obtener_valor(nodo)
    self.agregar_linea(f"{patron};")
