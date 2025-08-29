def visit_funcion(self, nodo):
    parametros = " ".join(nodo.parametros)
    self.agregar_linea(f"FUNC {nodo.nombre} {parametros}")
    self.indent += 1
    for ins in nodo.cuerpo:
        ins.aceptar(self)
    self.indent -= 1
    self.agregar_linea("ENDFUNC")
