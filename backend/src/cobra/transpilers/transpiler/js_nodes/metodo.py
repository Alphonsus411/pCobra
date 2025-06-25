def visit_metodo(self, nodo):
    """Transpila un método de clase, permitiendo anidación."""
    parametros = ", ".join(nodo.parametros)
    cuerpo = nodo.cuerpo
    if self.usa_indentacion is None:
        self.usa_indentacion = any(hasattr(ins, "variable") for ins in cuerpo)
    palabra = "async" if getattr(nodo, "asincronica", False) else ""
    espacio = " " if palabra else ""
    self.agregar_linea(f"{palabra}{espacio}{nodo.nombre}({parametros}) {{")
    if self.usa_indentacion:
        self.indentacion += 1
    for instruccion in cuerpo:
        if hasattr(instruccion, 'aceptar'):
            instruccion.aceptar(self)
        else:
            nombre = instruccion.__class__.__name__
            if nombre.startswith('Nodo'):
                nombre = nombre[4:]
            visit = getattr(self, f"visit_{nombre.lower()}", None)
            if visit:
                visit(instruccion)
    if self.usa_indentacion:
        self.indentacion -= 1
    self.agregar_linea("}")
