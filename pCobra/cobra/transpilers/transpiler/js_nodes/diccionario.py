def visit_diccionario(self, nodo):
    """Transpila un diccionario en JavaScript, permitiendo anidación."""
    elementos = getattr(nodo, "pares", getattr(nodo, "elementos", []))
    pares = ", ".join([
        f"{clave}: {self.visit_elemento(valor)}" for clave, valor in elementos
    ])
    self.agregar_linea(f"{{{pares}}}")
