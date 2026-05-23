def visit_asignacion(self, nodo):
    nombre = getattr(nodo, "identificador", nodo.variable)
    valor = self.obtener_valor(nodo.expresion)
    self.agregar_linea(f"var {nombre} = {valor};")

