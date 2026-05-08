from __future__ import annotations


def visit_garantia(self, nodo):
    condicion = self.obtener_valor(nodo.condicion)
    self.agregar_linea(f"if (!({condicion})) {{")
    self.indent += 1
    for instruccion in getattr(nodo, "bloque_escape", []):
        instruccion.aceptar(self)
    self.indent -= 1
    self.agregar_linea("}")
    for instruccion in getattr(nodo, "bloque_continuacion", []):
        instruccion.aceptar(self)
