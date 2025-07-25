def visit_clase(self, nodo):
    bases = ' '.join(getattr(nodo, 'bases', []))
    extra = f" {bases}" if bases else ""
    self.agregar_linea(f"CLASS {nodo.nombre}{extra}")
    self.indent += 1
    for m in nodo.metodos:
        m.aceptar(self)
    self.indent -= 1
    self.agregar_linea("ENDCLASS")
