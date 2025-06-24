def visit_para(self, nodo):
    iterable = self.obtener_valor(nodo.iterable)
    self.agregar_linea(f"PARA {nodo.variable} EN {iterable}")
    self.indent += 1
    for ins in nodo.cuerpo:
        ins.aceptar(self)
    self.indent -= 1
    self.agregar_linea("FINPARA")
