def visit_bucle_mientras(self, nodo):
    condicion = self.obtener_valor(nodo.condicion)
    self.agregar_linea(f"for {condicion} {{")
    self.indent += 1
    for inst in nodo.cuerpo:
        inst.aceptar(self)
    self.indent -= 1
    self.agregar_linea("}")

