def visit_lista(self, nodo):
    elementos = ", ".join(
        self.obtener_valor(elemento) for elemento in nodo.elementos
    )
    self.codigo += f"[{elementos}]\n"
