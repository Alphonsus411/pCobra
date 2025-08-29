def visit_asignacion(self, nodo):
    nombre = getattr(nodo, "identificador", nodo.variable)
    op = ":=" if hasattr(nodo, "variable") else "="
    valor = self.obtener_valor(nodo.expresion)
    self.agregar_linea(f"{nombre} {op} {valor}")

