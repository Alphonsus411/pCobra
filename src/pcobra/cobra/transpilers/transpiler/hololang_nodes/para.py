"""Bucle ``para`` específico para Hololang."""

from cobra.transpilers.semantica import procesar_bloque


def visit_para(self, nodo):
    """Transpila un ``para`` (foreach) a Hololang."""
    variable = self.obtener_valor(nodo.variable)
    iterable = self.obtener_valor(nodo.iterable)
    self.agregar_linea(f"foreach ({variable} in {iterable}) {{")
    procesar_bloque(self, nodo.cuerpo)
    self.agregar_linea("}")
