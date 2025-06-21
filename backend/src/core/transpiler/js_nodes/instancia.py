def visit_instancia(self, nodo):
    self.agregar_linea(f"{self.obtener_valor(nodo)};")
