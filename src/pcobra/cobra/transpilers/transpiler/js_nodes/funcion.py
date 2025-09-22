def visit_funcion(self, nodo):
    """Transpila una definición de función en JavaScript."""
    parametros = ", ".join(nodo.parametros)
    cuerpo = nodo.cuerpo
    if self.usa_indentacion is None:
        self.usa_indentacion = any(hasattr(ins, "variable") for ins in cuerpo)
    if getattr(nodo, "type_params", []):
        self.agregar_linea(
            f"// Generics {', '.join(nodo.type_params)} no soportados en JavaScript"
        )
    palabra = "async function" if getattr(nodo, "asincronica", False) else "function"
    self.agregar_linea(f"{palabra} {nodo.nombre}({parametros}) {{")
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
            instruccion.aceptar(self)
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
    for decorador in reversed(getattr(nodo, "decoradores", [])):
        expr = self.obtener_valor(decorador.expresion)
        self.agregar_linea(f"{nodo.nombre} = {expr}({nodo.nombre});")
