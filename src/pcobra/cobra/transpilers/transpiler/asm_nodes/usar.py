def visit_usar(self, nodo):
    self.agregar_linea(f"USAR {nodo.modulo}")
