def visit_funcion(self, nodo):
    for decorador in getattr(nodo, "decoradores", []):
        if hasattr(self, "visit_decorador"):
            self.visit_decorador(decorador)
    params = ", ".join(nodo.parametros)
    if getattr(nodo, "asincronica", False):
        self.agregar_linea(f"func {nodo.nombre}({params}) any {{")
    else:
        self.agregar_linea(f"func {nodo.nombre}({params}) {{")
    self.indent += 1
    for inst in nodo.cuerpo:
        inst.aceptar(self)
    self.indent -= 1
    self.agregar_linea("}")

    for decorador in reversed(getattr(nodo, "decoradores", [])):
        expr = self.obtener_valor(getattr(decorador, "expresion", decorador))
        self.agregar_linea(f"// decorador aplicado: {nodo.nombre} = {expr}({nodo.nombre})")
