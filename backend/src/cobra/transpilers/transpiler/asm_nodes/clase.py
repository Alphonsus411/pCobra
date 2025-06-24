def visit_clase(self, nodo):
    self.agregar_linea(f"CLASS {nodo.nombre}")
    self.indent += 1
    for m in nodo.metodos:
        m.aceptar(self)
    self.indent -= 1
    self.agregar_linea("ENDCLASS")
