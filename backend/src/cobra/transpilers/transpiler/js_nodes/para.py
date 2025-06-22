def visit_para(self, nodo):
    cuerpo = nodo.cuerpo
    if self.usa_indentacion is None:
        self.usa_indentacion = any(hasattr(ins, "variable") for ins in cuerpo)
    iterable = self.obtener_valor(nodo.iterable)
    self.agregar_linea(f"for (let {nodo.variable} of {iterable}) {{")
    if self.usa_indentacion:
        self.indentacion += 1
    for instruccion in cuerpo:
        instruccion.aceptar(self)
    if self.usa_indentacion:
        self.indentacion -= 1
    self.agregar_linea("}")
