"""Impresión en Hololang."""


def visit_imprimir(self, nodo):
    """Transpila la instrucción ``imprimir``."""
    valor = self.obtener_valor(nodo.expresion)
    self.agregar_linea(f"print({valor});")
