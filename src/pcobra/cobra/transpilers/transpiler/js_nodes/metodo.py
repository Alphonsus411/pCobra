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
    nombre_pila = f"__cobra_defer_stack_{self._defer_counter}"
    self._defer_counter += 1
    self._defer_stack.append(nombre_pila)
    self.agregar_linea(f"const {nombre_pila} = [];")
    self.agregar_linea("try {")
    if self.usa_indentacion:
        self.indentacion += 1
    if not cuerpo:
        self.agregar_linea(";")
    else:
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
    self.agregar_linea("} finally {")
    if self.usa_indentacion:
        self.indentacion += 1
    self.agregar_linea(f"while ({nombre_pila}.length) {{")
    if self.usa_indentacion:
        self.indentacion += 1
    self.agregar_linea(f"{nombre_pila}.pop()();")
    if self.usa_indentacion:
        self.indentacion -= 1
    self.agregar_linea("}")
    if self.usa_indentacion:
        self.indentacion -= 1
    self.agregar_linea("}")
    self._defer_stack.pop()
    if self.usa_indentacion:
        self.indentacion -= 1
    self.agregar_linea("}")
