def visit_condicional(self, nodo):
    bloque_si = getattr(nodo, "bloque_si", getattr(nodo, "cuerpo_si", []))
    bloque_sino = getattr(nodo, "bloque_sino", getattr(nodo, "cuerpo_sino", []))
    condicion = self.obtener_valor(nodo.condicion)
    self.agregar_linea(f"IF {condicion}")
    self.indent += 1
    for ins in bloque_si:
        ins.aceptar(self)
    self.indent -= 1
    if bloque_sino:
        self.agregar_linea("ELSE")
        self.indent += 1
        for ins in bloque_sino:
            ins.aceptar(self)
        self.indent -= 1
    self.agregar_linea("END")
