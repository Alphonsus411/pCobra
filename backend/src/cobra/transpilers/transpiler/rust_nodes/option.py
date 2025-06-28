from typing import Any


def visit_option(self, nodo: Any) -> None:
    valor = self.obtener_valor(nodo)
    self.agregar_linea(f"{valor};")
