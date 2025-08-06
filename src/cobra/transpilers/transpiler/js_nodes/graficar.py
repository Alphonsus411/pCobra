def visit_graficar(self, nodo):
    hb = self.obtener_valor(nodo.holobit)
    self.agregar_linea(f"graficar({hb});")
