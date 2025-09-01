from cobra.core.ast_nodes import NodoRetorno, NodoValor


def _inferir_tipo(expr):
    if isinstance(expr, NodoValor):
        if isinstance(expr.valor, bool):
            return "bool"
        if isinstance(expr.valor, int):
            return "i32"
        if isinstance(expr.valor, float):
            return "f64"
    return ""


def visit_funcion(self, nodo):
    parametros = ", ".join(nodo.parametros)
    genericos = (
        f"<{', '.join(nodo.type_params)}>" if getattr(nodo, "type_params", []) else ""
    )
    retorno = ""
    for inst in nodo.cuerpo:
        if isinstance(inst, NodoRetorno):
            tipo = _inferir_tipo(inst.expresion)
            if tipo and nodo.nombre != "main":
                retorno = f" -> {tipo}"
            break
    self.agregar_linea(f"fn {nodo.nombre}{genericos}({parametros}){retorno} {{")
    prev = getattr(self, "current_function", None)
    self.current_function = nodo.nombre
    self.indent += 1
    for instruccion in nodo.cuerpo:
        instruccion.aceptar(self)
    self.indent -= 1
    self.agregar_linea("}")
    self.current_function = prev
