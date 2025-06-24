def visit_lista(self, nodo):
    elems = ", ".join(self.obtener_valor(e) for e in nodo.elementos)
    self.agregar_linea(f"[{elems}]")
