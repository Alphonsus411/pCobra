def visit_retorno(self, nodo):
    valor = self.obtener_valor(nodo.expresion)
    if getattr(self, "current_function", "") == "main":
        self.agregar_linea(f"std::process::exit({valor});")
    else:
        self.agregar_linea(f"return {valor};")
