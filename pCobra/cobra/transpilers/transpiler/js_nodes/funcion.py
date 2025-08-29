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
    for instruccion in cuerpo:
        instruccion.aceptar(self)
    if self.usa_indentacion:
        self.indentacion -= 1
    self.agregar_linea("}")
    for decorador in reversed(getattr(nodo, "decoradores", [])):
        expr = self.obtener_valor(decorador.expresion)
        self.agregar_linea(f"{nodo.nombre} = {expr}({nodo.nombre});")
