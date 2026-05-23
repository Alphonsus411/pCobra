def visit_switch(self, nodo):
    if self.usa_indentacion is None:
        todos = []
        for c in nodo.casos:
            todos += c.cuerpo
        todos += nodo.por_defecto
        self.usa_indentacion = any(getattr(ins, "variable", None) for ins in todos)
    expr = self.obtener_valor(nodo.expresion)
    self.agregar_linea(f"switch ({expr}) {{")
    if self.usa_indentacion:
        self.indentacion += 1
    for caso in nodo.casos:
        val = self.obtener_valor(caso.valor)
        self.agregar_linea(f"case {val}:")
        if self.usa_indentacion:
            self.indentacion += 1
        for inst in caso.cuerpo:
            inst.aceptar(self)
        self.agregar_linea("break;")
        if self.usa_indentacion:
            self.indentacion -= 1
    if nodo.por_defecto:
        self.agregar_linea("default:")
        if self.usa_indentacion:
            self.indentacion += 1
        for inst in nodo.por_defecto:
            inst.aceptar(self)
        self.agregar_linea("break;")
        if self.usa_indentacion:
            self.indentacion -= 1
    if self.usa_indentacion:
        self.indentacion -= 1
    self.agregar_linea("}")
