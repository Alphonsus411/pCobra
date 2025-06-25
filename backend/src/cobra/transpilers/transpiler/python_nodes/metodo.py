def visit_metodo(self, nodo):
    parametros = ", ".join(nodo.parametros)
    prefijo = "async def" if getattr(nodo, "asincronica", False) else "def"
    self.codigo += (
        f"{self.obtener_indentacion()}{prefijo} {nodo.nombre}({parametros}):\n"
    )
    self.nivel_indentacion += 1
    for instruccion in nodo.cuerpo:
        instruccion.aceptar(self)
    self.nivel_indentacion -= 1
