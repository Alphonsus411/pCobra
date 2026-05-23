# Este nodo no genera salida directa; se maneja en visit_funcion

def visit_decorador(self, nodo):
    """Devuelve la expresión del decorador para uso posterior."""
    return self.obtener_valor(nodo.expresion)
