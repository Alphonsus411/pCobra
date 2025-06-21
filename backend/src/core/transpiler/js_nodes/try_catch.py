def visit_try_catch(self, nodo):
    self.agregar_linea("try {")
    if self.usa_indentacion:
        self.indentacion += 1
    for instruccion in nodo.bloque_try:
        instruccion.aceptar(self)
    if self.usa_indentacion:
        self.indentacion -= 1
    if nodo.bloque_catch:
        catch_var = nodo.nombre_excepcion or ""
        if self.usa_indentacion:
            self.agregar_linea(f"}} catch ({catch_var}) {{")
        else:
            self.agregar_linea("}")
            self.agregar_linea(f"catch ({catch_var}) {{")
        if self.usa_indentacion:
            self.indentacion += 1
        for instruccion in nodo.bloque_catch:
            instruccion.aceptar(self)
        if self.usa_indentacion:
            self.indentacion -= 1
        self.agregar_linea("}")
    else:
        self.agregar_linea("}")
