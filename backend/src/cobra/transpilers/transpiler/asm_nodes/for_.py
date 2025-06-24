def visit_for(self, nodo):
    iterable = self.obtener_valor(nodo.iterable)
    self.agregar_linea(f"FOR {nodo.variable} IN {iterable}")
    self.indent += 1
    for ins in nodo.cuerpo:
        ins.aceptar(self)
    self.indent -= 1
    self.agregar_linea("END")
