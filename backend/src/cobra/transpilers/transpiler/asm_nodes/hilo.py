def visit_hilo(self, nodo):
    args = ", ".join(self.obtener_valor(a) for a in nodo.llamada.argumentos)
    self.agregar_linea(f"THREAD {nodo.llamada.nombre} {args}")
