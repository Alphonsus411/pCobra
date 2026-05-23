def visit_condicional(self, nodo):
    """Transpila un 'if-else' con condiciones compuestas."""
    cuerpo_si = getattr(nodo, "cuerpo_si", getattr(nodo, "bloque_si", []))
    cuerpo_sino = getattr(nodo, "cuerpo_sino", getattr(nodo, "bloque_sino", []))
    if self.usa_indentacion is None:
        self.usa_indentacion = any(
            hasattr(ins, "variable") for ins in cuerpo_si + cuerpo_sino
        )
    condicion = self.obtener_valor(nodo.condicion)
    self.agregar_linea(f"if ({condicion}) {{")
    if self.usa_indentacion:
        self.indentacion += 1
    for instruccion in cuerpo_si:
        instruccion.aceptar(self)
    if self.usa_indentacion:
        self.indentacion -= 1
    if cuerpo_sino:
        if self.usa_indentacion:
            self.agregar_linea("} else {")
        else:
            self.agregar_linea("}")
            self.agregar_linea("else {")
        if self.usa_indentacion:
            self.indentacion += 1
        for instruccion in cuerpo_sino:
            instruccion.aceptar(self)
        if self.usa_indentacion:
            self.indentacion -= 1
        self.agregar_linea("}")
    else:
        self.agregar_linea("}")
