"""Bucle 'para' para Hololang."""

from pcobra.cobra.transpilers.semantica import procesar_bloque


def visit_for(self, nodo):
    """Transpila un bucle ``for`` a Hololang."""
    variable = self.obtener_valor(nodo.variable)
    iterable = self.obtener_valor(nodo.iterable)
    self.agregar_linea(f"for ({variable} in {iterable}) {{")
    procesar_bloque(self, nodo.cuerpo)
    self.agregar_linea("}")
