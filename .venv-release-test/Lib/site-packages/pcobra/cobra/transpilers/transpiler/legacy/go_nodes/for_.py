def visit_for(self, nodo):
    iterable = self.obtener_valor(nodo.iterable)
    self.agregar_linea(f"for _, {nodo.variable} := range {iterable} {{")
    self.indent += 1
    for inst in nodo.cuerpo:
        inst.aceptar(self)
    self.indent -= 1
    self.agregar_linea("}")

