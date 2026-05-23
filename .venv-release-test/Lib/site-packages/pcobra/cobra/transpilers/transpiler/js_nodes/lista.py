def visit_lista(self, nodo):
    """Transpila una lista en JavaScript, permitiendo anidación."""
    elementos = ", ".join(self.visit_elemento(e) for e in nodo.elementos)
    self.agregar_linea(f"[{elementos}]")
