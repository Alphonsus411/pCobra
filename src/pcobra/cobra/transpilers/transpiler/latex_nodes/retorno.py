"""Nodo de retorno para el transpilador a LaTeX."""

def visit_retorno(self, nodo):
    """Genera la instrucción de retorno en LaTeX."""
    valor = self.obtener_valor(nodo.expresion)
    self.agregar_linea(f"return {valor}")
