"""Nodo de bucle 'mientras' para Hololang."""

from cobra.transpilers.semantica import procesar_bloque


def visit_bucle_mientras(self, nodo):
    """Transpila un bucle mientras a Hololang."""
    condicion = self.obtener_valor(nodo.condicion)
    self.agregar_linea(f"while ({condicion}) {{")
    procesar_bloque(self, nodo.cuerpo)
    self.agregar_linea("}")
