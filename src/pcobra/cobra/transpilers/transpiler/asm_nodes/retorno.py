def visit_retorno(self, nodo):
    valor = self.obtener_valor(nodo.expresion)
    self.agregar_linea(f"RETURN {valor}")
