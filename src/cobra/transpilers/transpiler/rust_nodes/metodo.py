def visit_metodo(self, nodo):
    parametros = ", ".join(nodo.parametros)
    self.agregar_linea(f"fn {nodo.nombre}({parametros}) {{")
    self.indent += 1
    for instruccion in nodo.cuerpo:
        instruccion.aceptar(self)
    self.indent -= 1
    self.agregar_linea("}")
