def visit_condicional(self, nodo):
    cuerpo_si = getattr(nodo, "cuerpo_si", getattr(nodo, "bloque_si", []))
    cuerpo_sino = getattr(nodo, "cuerpo_sino", getattr(nodo, "bloque_sino", []))
    condicion = self.obtener_valor(nodo.condicion)
    self.agregar_linea(f"if ({condicion}) {{")
    self.indent += 1
    for instruccion in cuerpo_si:
        instruccion.aceptar(self)
    self.indent -= 1
    if cuerpo_sino:
        self.agregar_linea("} else {")
        self.indent += 1
        for instruccion in cuerpo_sino:
            instruccion.aceptar(self)
        self.indent -= 1
        self.agregar_linea("}")
    else:
        self.agregar_linea("}")
