def visit_clase(self, nodo):
    bases = getattr(nodo, 'bases', [])
    base = f" : public {bases[0]}" if bases else ""
    extra = f" // bases: {', '.join(bases)}" if len(bases) > 1 else ""
    self.agregar_linea(f"class {nodo.nombre}{base}{extra} {{")
    self.indent += 1
    for metodo in getattr(nodo, 'metodos', []):
        metodo.aceptar(self)
    self.indent -= 1
    self.agregar_linea("};")
