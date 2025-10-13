from pcobra.cobra.transpilers.semantica import datos_asignacion

def visit_asignacion(self, nodo):
    nombre, valor, _ = datos_asignacion(self, nodo)
    self.agregar_linea(f"{nombre} = {valor};")
