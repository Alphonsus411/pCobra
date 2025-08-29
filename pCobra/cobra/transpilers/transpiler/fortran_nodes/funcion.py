
def visit_funcion(self, nodo):
    params = ", ".join(nodo.parametros)
    self.agregar_linea(f"subroutine {nodo.nombre}({params})")
    self.indent += 1
    for inst in nodo.cuerpo:
        inst.aceptar(self)
    self.indent -= 1
    self.agregar_linea("end subroutine")
