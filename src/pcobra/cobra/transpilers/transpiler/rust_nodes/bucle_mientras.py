from pcobra.cobra.transpilers.semantica import procesar_bloque


def visit_bucle_mientras(self, nodo):
    cuerpo = nodo.cuerpo
    condicion = self.obtener_valor(nodo.condicion)
    self.agregar_linea(f"while {condicion} {{")
    with self._enum_scope(cuerpo):
        procesar_bloque(self, cuerpo)
    self.agregar_linea("}")
