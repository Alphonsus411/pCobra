from pcobra.core.ast_nodes import NodoRetorno


def visit_funcion(self, nodo):
    """Genera una función, subrutina o programa principal en Fortran."""
    params = ", ".join(nodo.parametros)
    tiene_retorno = any(isinstance(inst, NodoRetorno) for inst in nodo.cuerpo)
    if nodo.nombre == "main":
        self.agregar_linea("program main")
        self.indent += 1
        self.in_main = True
        for inst in nodo.cuerpo:
            inst.aceptar(self)
        self.in_main = False
        self.indent -= 1
        self.agregar_linea("end program main")
    elif tiene_retorno:
        self.agregar_linea(f"function {nodo.nombre}({params}) result(r)")
        self.indent += 1
        self.current_result = "r"
        for inst in nodo.cuerpo:
            inst.aceptar(self)
        self.current_result = None
        self.indent -= 1
        self.agregar_linea("end function")
    else:
        self.agregar_linea(f"subroutine {nodo.nombre}({params})")
        self.indent += 1
        for inst in nodo.cuerpo:
            inst.aceptar(self)
        self.indent -= 1
        self.agregar_linea("end subroutine")
