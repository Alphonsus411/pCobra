
def visit_condicional(self, nodo):
    bloque_si = getattr(nodo, "bloque_si", getattr(nodo, "cuerpo_si", []))
    bloque_sino = getattr(nodo, "bloque_sino", getattr(nodo, "cuerpo_sino", []))
    condicion = self.obtener_valor(nodo.condicion)
    self.codigo += f"{self.obtener_indentacion()}if {condicion}:\n"
    self.nivel_indentacion += 1
    for instruccion in bloque_si:
        instruccion.aceptar(self)
    self.nivel_indentacion -= 1
    if bloque_sino:
        self.codigo += f"{self.obtener_indentacion()}else:\n"
        self.nivel_indentacion += 1
        for instruccion in bloque_sino:
            instruccion.aceptar(self)
        self.nivel_indentacion -= 1
