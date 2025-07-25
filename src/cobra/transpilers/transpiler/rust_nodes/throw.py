from typing import Any


def visit_throw(self, nodo: Any) -> None:
    valor = self.obtener_valor(nodo.expresion)
    self.agregar_linea(f"return Err({valor}.into());")
