def visit_imprimir(self, nodo):
    valor = self.obtener_valor(getattr(nodo, "expresion", nodo))
    self.codigo += f"{self.obtener_indentacion()}print({valor})\n"
