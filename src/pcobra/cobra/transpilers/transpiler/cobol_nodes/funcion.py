
def visit_funcion(self, nodo):
    self.agregar_linea(f"{nodo.nombre} SECTION.")
    self.indent += 1
    for inst in nodo.cuerpo:
        inst.aceptar(self)
    self.indent -= 1
    self.agregar_linea("EXIT SECTION.")
