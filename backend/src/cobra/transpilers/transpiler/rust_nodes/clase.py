def visit_clase(self, nodo):
    bases = getattr(nodo, 'bases', [])
    extra = f" // bases: {', '.join(bases)}" if bases else ""
    self.agregar_linea(f"struct {nodo.nombre} {{}}{extra}")
    self.agregar_linea("")
    self.agregar_linea(f"impl {nodo.nombre} {{")
    self.indent += 1
    for metodo in getattr(nodo, 'metodos', []):
        metodo.aceptar(self)
    self.indent -= 1
    self.agregar_linea("}")
