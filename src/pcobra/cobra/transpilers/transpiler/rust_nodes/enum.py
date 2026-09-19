def visit_enum(self, nodo):
    self.agregar_linea(f"enum {nodo.nombre} {{")
    self.indent += 1
    for miembro in nodo.miembros:
        self.agregar_linea(f"{miembro},")
    self.indent -= 1
    self.agregar_linea("}")
