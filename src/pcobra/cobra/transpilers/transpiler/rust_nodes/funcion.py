from pcobra.cobra.core.ast_nodes import NodoRetorno, NodoValor


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
    for decorador in getattr(nodo, "decoradores", []):
        self.visit_decorador(decorador)
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

    prefijo = "async fn" if getattr(nodo, "asincronica", False) else "fn"
    self.agregar_linea(f"{prefijo} {nodo.nombre}{genericos}({parametros}){retorno} {{")
    prev = getattr(self, "current_function", None)
    prev_enum_names = self._enum_names
    self.current_function = nodo.nombre
    self._enum_names = prev_enum_names | self._direct_enum_names(nodo.cuerpo)
    self.indent += 1
    try:
        for instruccion in nodo.cuerpo:
            instruccion.aceptar(self)
    finally:
        self.indent -= 1
        self._enum_names = prev_enum_names
        self.current_function = prev
    self.agregar_linea("}")

    for decorador in reversed(getattr(nodo, "decoradores", [])):
        decorador_expr = self.obtener_valor(getattr(decorador, "expresion", decorador))
        self.agregar_linea(
            f"// decorador aplicado: {nodo.nombre} = {decorador_expr}({nodo.nombre})"
        )
