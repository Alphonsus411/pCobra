"""Declaraciones de retorno en Hololang."""


def visit_retorno(self, nodo):
    """Transpila un ``retorno``."""
    if nodo.expresion is None:
        self.agregar_linea("return;")
    else:
        valor = self.obtener_valor(nodo.expresion)
        self.agregar_linea(f"return {valor};")
