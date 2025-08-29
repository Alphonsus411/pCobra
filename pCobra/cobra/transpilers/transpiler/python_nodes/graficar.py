def visit_graficar(self, nodo):
    hb = self.obtener_valor(nodo.holobit)
    self.codigo += f"{self.obtener_indentacion()}graficar({hb})\n"
