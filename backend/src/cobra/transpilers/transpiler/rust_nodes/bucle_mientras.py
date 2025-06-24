def visit_bucle_mientras(self, nodo):
    cuerpo = nodo.cuerpo
    condicion = self.obtener_valor(nodo.condicion)
    self.agregar_linea(f"while {condicion} {{")
    self.indent += 1
    for instr in cuerpo:
        instr.aceptar(self)
    self.indent -= 1
    self.agregar_linea("}")
