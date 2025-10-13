from pcobra.core.ast_nodes import NodoRetorno


def visit_funcion(self, nodo):
    params = ", ".join(nodo.parametros)
    has_return = any(isinstance(inst, NodoRetorno) for inst in nodo.cuerpo)
    if has_return:
        self.agregar_linea(f"function resultado = {nodo.nombre}({params})")
    else:
        self.agregar_linea(f"function {nodo.nombre}({params})")
    self.indent += 1
    for inst in nodo.cuerpo:
        inst.aceptar(self)
    self.indent -= 1
    self.agregar_linea("end")
