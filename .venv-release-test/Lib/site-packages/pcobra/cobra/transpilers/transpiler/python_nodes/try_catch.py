def visit_try_catch(self, nodo):
    self.codigo += f"{self.obtener_indentacion()}try:\n"
    self.nivel_indentacion += 1
    for instruccion in nodo.bloque_try:
        instruccion.aceptar(self)
    self.nivel_indentacion -= 1
    if nodo.bloque_catch:
        nombre = f" as {nodo.nombre_excepcion}" if nodo.nombre_excepcion else ""
        self.codigo += f"{self.obtener_indentacion()}except Exception{nombre}:\n"
        self.nivel_indentacion += 1
        for instruccion in nodo.bloque_catch:
            instruccion.aceptar(self)
        self.nivel_indentacion -= 1
