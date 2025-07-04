from ...semantica import procesar_bloque

def visit_for(self, nodo):
    iterable = self.obtener_valor(nodo.iterable)
    self.codigo += (
        f"{self.obtener_indentacion()}for {nodo.variable} in {iterable}:\n"
    )
    procesar_bloque(self, nodo.cuerpo)
