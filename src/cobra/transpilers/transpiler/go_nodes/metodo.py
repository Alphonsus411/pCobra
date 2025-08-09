def visit_metodo(self, nodo):
    params = ", ".join(nodo.parametros)
    clase = getattr(nodo, "nombre_clase", "")
    receptor = f"(self *{clase}) " if clase else ""
    self.agregar_linea(f"func {receptor}{nodo.nombre}({params}) {{")
    self.indent += 1
    for inst in nodo.cuerpo:
        inst.aceptar(self)
    self.indent -= 1
    self.agregar_linea("}")

