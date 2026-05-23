def visit_retorno(self, nodo):
    if getattr(nodo, "expresion", None) is not None:
        valor = self.obtener_valor(nodo.expresion)
        self.agregar_linea(f"return {valor};")
    else:
        self.agregar_linea("return;")
