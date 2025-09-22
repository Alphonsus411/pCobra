from cobra.transpilers.semantica import procesar_bloque

def visit_para(self, nodo):
    cuerpo = nodo.cuerpo
    if self.usa_indentacion is None:
        self.usa_indentacion = any(hasattr(ins, "variable") for ins in cuerpo)
    iterable = self.obtener_valor(nodo.iterable)
    prefijo = "for await" if getattr(nodo, "asincronico", False) else "for"
    self.agregar_linea(f"{prefijo} (let {nodo.variable} of {iterable}) {{")
    procesar_bloque(self, cuerpo)
    self.agregar_linea("}")
