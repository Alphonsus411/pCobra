def visit_switch(self, nodo):
    expr = self.obtener_valor(nodo.expresion)
    self.agregar_linea(f"switch ({expr}) {{")
    self.indent += 1
    for caso in nodo.casos:
        val = self.obtener_valor(caso.valor)
        self.agregar_linea(f"case {val}:")
        self.indent += 1
        for inst in caso.cuerpo:
            inst.aceptar(self)
        self.agregar_linea("break;")
        self.indent -= 1
    if nodo.por_defecto:
        self.agregar_linea("default:")
        self.indent += 1
        for inst in nodo.por_defecto:
            inst.aceptar(self)
        self.agregar_linea("break;")
        self.indent -= 1
    self.indent -= 1
    self.agregar_linea("}")
