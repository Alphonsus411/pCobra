from cobra.transpilers.semantica import datos_asignacion

def visit_asignacion(self, nodo):
    nombre, valor, es_attr = datos_asignacion(self, nodo)
    if es_attr:
        self.agregar_linea(f"{nombre} = {valor};")
    else:
        self.agregar_linea(f"auto {nombre} = {valor};")
