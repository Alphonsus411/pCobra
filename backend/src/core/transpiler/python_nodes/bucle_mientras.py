def visit_bucle_mientras(self, nodo):
    condicion = self.obtener_valor(nodo.condicion)
    self.codigo += f"{self.obtener_indentacion()}while {condicion}:\n"
    self.nivel_indentacion += 1
    for instruccion in nodo.cuerpo:
        instruccion.aceptar(self)
    self.nivel_indentacion -= 1
