def visit_bucle_mientras(self, nodo):
    """Transpila un bucle 'while' en JavaScript, permitiendo anidación."""
    cuerpo = nodo.cuerpo
    if self.usa_indentacion is None:
        self.usa_indentacion = any(hasattr(ins, "variable") for ins in cuerpo)
    condicion = self.obtener_valor(nodo.condicion)
    self.agregar_linea(f"while ({condicion}) {{")
    if self.usa_indentacion:
        self.indentacion += 1
    for instruccion in cuerpo:
        instruccion.aceptar(self)
    if self.usa_indentacion:
        self.indentacion -= 1
    self.agregar_linea("}")
