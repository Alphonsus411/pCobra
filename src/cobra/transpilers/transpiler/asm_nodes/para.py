from cobra.transpilers.semantica import procesar_bloque

def visit_para(self, nodo):
    iterable = self.obtener_valor(nodo.iterable)
    self.agregar_linea(f"PARA {nodo.variable} EN {iterable}")
    procesar_bloque(self, nodo.cuerpo)
    self.agregar_linea("FINPARA")
