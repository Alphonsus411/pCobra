def visit_funcion(self, nodo):
    parametros = ", ".join(f"auto {p}" for p in nodo.parametros)
    self.agregar_linea(f"void {nodo.nombre}({parametros}) {{")
    self.indent += 1
    for instruccion in nodo.cuerpo:
        instruccion.aceptar(self)
    self.indent -= 1
    self.agregar_linea("}")
