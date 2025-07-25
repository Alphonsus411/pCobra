from src.cobra.transpilers.semantica import datos_asignacion

def visit_asignacion(self, nodo):
    nombre, valor, _ = datos_asignacion(self, nodo)
    self.codigo += f"{self.obtener_indentacion()}{nombre} = {valor}\n"
