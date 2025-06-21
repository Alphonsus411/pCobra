def visit_for(self, nodo):
    iterable = self.obtener_valor(nodo.iterable)
    self.codigo += (
        f"{self.obtener_indentacion()}for {nodo.variable} in "
        f"{iterable}:\n"
    )
    self.nivel_indentacion += 1
    for instruccion in nodo.cuerpo:
        instruccion.aceptar(self)
    self.nivel_indentacion -= 1
