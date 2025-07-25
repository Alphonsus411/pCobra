from src.cobra.transpilers.semantica import procesar_bloque

def visit_bucle_mientras(self, nodo):
    condicion = self.obtener_valor(nodo.condicion)
    self.codigo += f"{self.obtener_indentacion()}while {condicion}:\n"
    procesar_bloque(self, nodo.cuerpo)
