def visit_funcion(self, nodo):
    for decorador in getattr(nodo, "decoradores", []):
        if hasattr(self, "visit_decorador"):
            self.visit_decorador(decorador)
    params = ", ".join(nodo.parametros)
    self.agregar_linea(f"static void {nodo.nombre}({params}) {{")
    self.indent += 1
    for inst in nodo.cuerpo:
        inst.aceptar(self)
    self.indent -= 1
    self.agregar_linea("}")
