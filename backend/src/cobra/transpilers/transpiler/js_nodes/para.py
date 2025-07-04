from ...semantica import procesar_bloque

def visit_para(self, nodo):
    cuerpo = nodo.cuerpo
    if self.usa_indentacion is None:
        self.usa_indentacion = any(hasattr(ins, "variable") for ins in cuerpo)
    iterable = self.obtener_valor(nodo.iterable)
    self.agregar_linea(f"for (let {nodo.variable} of {iterable}) {{")
    procesar_bloque(self, cuerpo)
    self.agregar_linea("}")
