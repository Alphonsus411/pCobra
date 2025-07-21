from src.cobra.transpilers.semantica import procesar_bloque

def visit_for(self, nodo):
    iterable = self.obtener_valor(nodo.iterable)
    self.agregar_linea(f"FOR {nodo.variable} IN {iterable}")
    procesar_bloque(self, nodo.cuerpo)
    self.agregar_linea("END")
