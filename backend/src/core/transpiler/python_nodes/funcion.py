def visit_funcion(self, nodo):
    parametros = ", ".join(nodo.parametros)
    self.codigo += (
        f"{self.obtener_indentacion()}def {nodo.nombre}({parametros}):\n"
    )
    self.nivel_indentacion += 1
    for instruccion in nodo.cuerpo:
        instruccion.aceptar(self)
    self.nivel_indentacion -= 1
