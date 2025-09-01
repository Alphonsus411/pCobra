def visit_instancia(self, nodo):
    args = ", ".join(self.obtener_valor(a) for a in nodo.argumentos)
    self.agregar_linea(f"NEW {nodo.nombre_clase} {args}")
