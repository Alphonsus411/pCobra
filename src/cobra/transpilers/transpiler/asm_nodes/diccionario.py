def visit_diccionario(self, nodo):
    pares = ", ".join(
        f"{self.obtener_valor(k)}:{self.obtener_valor(v)}" for k, v in nodo.elementos
    )
    self.agregar_linea(f"{{{pares}}}")
