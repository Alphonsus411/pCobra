from pcobra.cobra.transpilers.semantica import procesar_bloque


def visit_bucle_mientras(self, nodo):
    if nodo is None:
        raise ValueError("El nodo no puede ser None")

    try:
        condicion = self.obtener_valor(nodo.condicion)
        self.agregar_linea(f"WHILE {condicion}")
        self.indent += 1
        procesar_bloque(self, nodo.cuerpo)
        self.indent -= 1
        self.agregar_linea("END")
    except Exception as e:
        raise ValueError(f"Error al procesar bucle mientras: {str(e)}")