from __future__ import annotations


def visit_garantia(self, nodo):
    condicion = self.obtener_valor(nodo.condicion)
    self.codigo += f"{self.obtener_indentacion()}if not {condicion}:\n"
    self.nivel_indentacion += 1
    if getattr(nodo, "bloque_escape", None):
        for instruccion in nodo.bloque_escape:
            instruccion.aceptar(self)
    else:
        self.codigo += f"{self.obtener_indentacion()}pass\n"
    self.nivel_indentacion -= 1
    for instruccion in getattr(nodo, "bloque_continuacion", []):
        instruccion.aceptar(self)
