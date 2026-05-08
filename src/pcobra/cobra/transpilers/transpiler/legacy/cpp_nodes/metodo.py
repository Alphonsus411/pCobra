def visit_metodo(self, nodo):
    parametros = ", ".join(f"auto {p}" for p in nodo.parametros)
    self.agregar_linea(f"auto {nodo.nombre}({parametros}) {{")
    self.indent += 1
    for instruccion in nodo.cuerpo:
        instruccion.aceptar(self)
    self.indent -= 1
    self.agregar_linea("}")
