from ...semantica import procesar_bloque

def visit_bucle_mientras(self, nodo):
    condicion = self.obtener_valor(nodo.condicion)
    self.agregar_linea(f"WHILE {condicion}")
    procesar_bloque(self, nodo.cuerpo)
    self.agregar_linea("END")
