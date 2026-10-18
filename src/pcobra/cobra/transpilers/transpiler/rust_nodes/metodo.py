def visit_metodo(self, nodo):
    parametros_nodo = list(nodo.parametros)
    if parametros_nodo[:1] in (["este"], ["self"]):
        parametros_nodo = ["&self", *parametros_nodo[1:]]
    if len(parametros_nodo) > 1:
        raise NotImplementedError(
            f"POO Rust no soporta parámetros tipados en el método '{nodo.nombre}'; "
            "el subconjunto actual admite únicamente el receptor."
        )
    parametros = ", ".join(parametros_nodo)
    genericos = (
        f"<{', '.join(nodo.type_params)}>" if getattr(nodo, "type_params", []) else ""
    )
    self.agregar_linea(f"fn {nodo.nombre}{genericos}({parametros}) {{")
    self.indent += 1
    with self._enum_scope(nodo.cuerpo):
        for instruccion in nodo.cuerpo:
            instruccion.aceptar(self)
    self.indent -= 1
    self.agregar_linea("}")
