def visit_defer(self, nodo):
    if not getattr(self, "_defer_stack", None):
        expresion = self.obtener_valor(nodo.expresion)
        self.agregar_linea(f"// defer fuera de contexto: {expresion};")
        return

    nombre_pila = self._defer_stack[-1]
    expresion = self.obtener_valor(nodo.expresion)
    self.agregar_linea(f"{nombre_pila}.push(() => {expresion});")
