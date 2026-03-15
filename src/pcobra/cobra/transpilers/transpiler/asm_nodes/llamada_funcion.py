def visit_llamada_funcion(self, nodo):
    args = " ".join(self.obtener_valor(arg) for arg in getattr(nodo, "argumentos", []))
    sufijo = f" {args}" if args else ""
    self.agregar_linea(f"CALL {nodo.nombre}{sufijo}")
