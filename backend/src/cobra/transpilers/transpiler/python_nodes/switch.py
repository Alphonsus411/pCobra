def visit_switch(self, nodo):
    expr = self.obtener_valor(nodo.expresion)
    self.codigo += f"{self.obtener_indentacion()}match {expr}:\n"
    self.nivel_indentacion += 1
    for caso in nodo.casos:
        val = self.obtener_valor(caso.valor)
        self.codigo += f"{self.obtener_indentacion()}case {val}:\n"
        self.nivel_indentacion += 1
        for inst in caso.cuerpo:
            inst.aceptar(self)
        self.nivel_indentacion -= 1
    if nodo.por_defecto:
        self.codigo += f"{self.obtener_indentacion()}case _:\n"
        self.nivel_indentacion += 1
        for inst in nodo.por_defecto:
            inst.aceptar(self)
        self.nivel_indentacion -= 1
    self.nivel_indentacion -= 1
