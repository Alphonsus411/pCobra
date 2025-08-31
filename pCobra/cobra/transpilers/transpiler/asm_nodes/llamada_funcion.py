def visit_llamada_funcion(self, nodo):
    # Por ahora se ignoran los argumentos y se realiza una llamada directa
    self.agregar_linea(f"call {nodo.nombre}")
