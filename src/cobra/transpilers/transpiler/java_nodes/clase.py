def visit_clase(self, nodo):
    metodos = getattr(nodo, "metodos", getattr(nodo, "cuerpo", []))
    self.agregar_linea(f"class {nodo.nombre} {{")
    self.indent += 1
    for metodo in metodos:
        metodo.aceptar(self)
    self.indent -= 1
    self.agregar_linea("}")

