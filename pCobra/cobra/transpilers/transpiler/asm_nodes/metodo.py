def visit_metodo(self, nodo):
    params = " ".join(nodo.parametros)
    self.agregar_linea(f"METHOD {nodo.nombre} {params}")
    self.indent += 1
    for ins in nodo.cuerpo:
        ins.aceptar(self)
    self.indent -= 1
    self.agregar_linea("ENDMETHOD")
