def visit_imprimir(self, nodo):
    valor = self.obtener_valor(nodo.expresion)
    self.agregar_linea(f"console.log({valor});")
