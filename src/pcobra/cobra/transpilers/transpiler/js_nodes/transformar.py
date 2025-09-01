def visit_transformar(self, nodo):
    hb = self.obtener_valor(nodo.holobit)
    op = self.obtener_valor(nodo.operacion)
    params = ", ".join(self.obtener_valor(p) for p in nodo.parametros)
    argumentos = ", ".join(filter(None, [hb, op, params]))
    self.agregar_linea(f"transformar({argumentos});")
