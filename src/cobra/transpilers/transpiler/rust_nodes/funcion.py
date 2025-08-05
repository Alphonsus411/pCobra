def visit_funcion(self, nodo):
    parametros = ", ".join(nodo.parametros)
    genericos = (
        f"<{', '.join(nodo.type_params)}>" if getattr(nodo, "type_params", []) else ""
    )
    self.agregar_linea(f"fn {nodo.nombre}{genericos}({parametros}) {{")
    self.indent += 1
    for instruccion in nodo.cuerpo:
        instruccion.aceptar(self)
    self.indent -= 1
    self.agregar_linea("}")
