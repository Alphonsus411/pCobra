
def visit_llamada_funcion(self, nodo):
    args = " ".join(self.obtener_valor(a) for a in nodo.argumentos)
    if args:
        self.agregar_linea(f"CALL '{nodo.nombre}' USING {args}")
    else:
        self.agregar_linea(f"CALL '{nodo.nombre}'")
