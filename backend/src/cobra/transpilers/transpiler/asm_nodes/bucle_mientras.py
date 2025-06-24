def visit_bucle_mientras(self, nodo):
    condicion = self.obtener_valor(nodo.condicion)
    self.agregar_linea(f"WHILE {condicion}")
    self.indent += 1
    for ins in nodo.cuerpo:
        ins.aceptar(self)
    self.indent -= 1
    self.agregar_linea("END")
