def visit_funcion(self, nodo):
    previo = self.current
    previa_indent = self.indent
    cuerpo: list[str] = []
    self.current = cuerpo
    self.indent = 1
    for ins in nodo.cuerpo:
        ins.aceptar(self)
    self.current = previo
    self.indent = previa_indent
    cuerpo_code = "\n".join(cuerpo)
    self.functions.append(f"{nodo.nombre}:\n{cuerpo_code}\n    ret")
