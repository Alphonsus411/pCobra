def visit_hilo(self, nodo):
    args = ", ".join(self.obtener_valor(a) for a in nodo.llamada.argumentos)
    self.agregar_linea(f"Promise.resolve().then(() => {nodo.llamada.nombre}({args}));")
