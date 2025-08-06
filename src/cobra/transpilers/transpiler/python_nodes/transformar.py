def visit_transformar(self, nodo):
    hb = self.obtener_valor(nodo.holobit)
    op = self.obtener_valor(nodo.operacion)
    params = ", ".join(self.obtener_valor(p) for p in nodo.parametros)
    argumentos = f"{hb}, {op}" + (", " + params if params else "")
    self.codigo += f"{self.obtener_indentacion()}transformar({argumentos})\n"
