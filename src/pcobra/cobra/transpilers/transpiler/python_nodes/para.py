from pcobra.cobra.transpilers.semantica import procesar_bloque

def visit_para(self, nodo):
    iterable = self.obtener_valor(nodo.iterable)
    palabra = "async for" if getattr(nodo, "asincronico", False) else "for"
    self.codigo += (
        f"{self.obtener_indentacion()}{palabra} {nodo.variable} in {iterable}:\n"
    )
    procesar_bloque(self, nodo.cuerpo)
