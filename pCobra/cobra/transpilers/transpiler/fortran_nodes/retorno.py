def visit_retorno(self, nodo):
    """Maneja la instrucción de retorno en Fortran."""
    if getattr(self, "in_main", False):
        if getattr(nodo, "expresion", None) is not None:
            valor = self.obtener_valor(nodo.expresion)
            self.agregar_linea(f"print *, {valor}")
    elif getattr(self, "current_result", None):
        if getattr(nodo, "expresion", None) is not None:
            valor = self.obtener_valor(nodo.expresion)
            self.agregar_linea(f"{self.current_result} = {valor}")
        self.agregar_linea("return")
    else:
        self.agregar_linea("return")
