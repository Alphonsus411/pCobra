def visit_defer(self, nodo):
    if not getattr(self, "_defer_stack", None):
        expresion = self.obtener_valor(nodo.expresion)
        self.codigo += (
            f"{self.obtener_indentacion()}# defer fuera de contexto: {expresion}\n"
        )
        return

    nombre_pila = self._defer_stack[-1]
    expresion = self.obtener_valor(nodo.expresion)
    self.codigo += (
        f"{self.obtener_indentacion()}{nombre_pila}.callback(lambda: {expresion})\n"
    )
