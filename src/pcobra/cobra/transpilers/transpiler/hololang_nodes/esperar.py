"""Expresiones ``await`` en Hololang."""


def visit_esperar(self, nodo):
    """Transpila la espera de una operación asíncrona."""
    self.requiere_async = True
    expresion = self.obtener_valor(nodo.expresion)
    self.agregar_linea(f"await {expresion};")
