from core.ast_nodes import NodoRetorno


def visit_funcion(self, nodo):
    if getattr(nodo, "type_params", []):
        genericos = ", ".join(f"typename {t}" for t in nodo.type_params)
        self.agregar_linea(f"template <{genericos}>")
    parametros = ", ".join(f"auto {p}" for p in nodo.parametros)
    tiene_retorno = any(isinstance(inst, NodoRetorno) for inst in nodo.cuerpo)
    if tiene_retorno:
        tipo = "int" if nodo.nombre == "main" else "auto"
    else:
        tipo = "void"
    self.agregar_linea(f"{tipo} {nodo.nombre}({parametros}) {{")
    self.indent += 1
    for instruccion in nodo.cuerpo:
        instruccion.aceptar(self)
    self.indent -= 1
    self.agregar_linea("}")
