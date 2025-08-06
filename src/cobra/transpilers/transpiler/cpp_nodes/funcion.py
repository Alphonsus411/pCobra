def visit_funcion(self, nodo):
    if getattr(nodo, "type_params", []):
        genericos = ", ".join(f"typename {t}" for t in nodo.type_params)
        self.agregar_linea(f"template <{genericos}>")
    parametros = ", ".join(f"auto {p}" for p in nodo.parametros)
    self.agregar_linea(f"void {nodo.nombre}({parametros}) {{")
    self.indent += 1
    for instruccion in nodo.cuerpo:
        instruccion.aceptar(self)
    self.indent -= 1
    self.agregar_linea("}")
