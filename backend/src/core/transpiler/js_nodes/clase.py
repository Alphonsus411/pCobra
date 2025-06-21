def visit_clase(self, nodo):
    """Transpila una clase en JavaScript, admitiendo métodos y clases anidados."""
    metodos = getattr(nodo, "cuerpo", getattr(nodo, "metodos", []))
    if self.usa_indentacion is None:
        self.usa_indentacion = any(hasattr(m, "variable") for m in metodos)
    self.agregar_linea(f"class {nodo.nombre} {{")
    if self.usa_indentacion:
        self.indentacion += 1
    for metodo in metodos:
        metodo.aceptar(self)
    if self.usa_indentacion:
        self.indentacion -= 1
    self.agregar_linea("}")
