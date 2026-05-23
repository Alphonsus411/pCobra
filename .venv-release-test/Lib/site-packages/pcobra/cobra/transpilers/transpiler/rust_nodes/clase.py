def visit_clase(self, nodo):
    bases = getattr(nodo, 'bases', [])
    extra = f" // bases: {', '.join(bases)}" if bases else ""
    genericos = (
        f"<{', '.join(nodo.type_params)}>" if getattr(nodo, "type_params", []) else ""
    )
    self.agregar_linea(f"struct {nodo.nombre}{genericos} {{}}{extra}")
    self.agregar_linea("")
    self.agregar_linea(f"impl{genericos} {nodo.nombre}{genericos} {{")
    self.indent += 1
    for metodo in getattr(nodo, 'metodos', []):
        metodo.aceptar(self)
    self.indent -= 1
    self.agregar_linea("}")
