from __future__ import annotations


def visit_garantia(self, nodo):
    cuerpo_normal = getattr(nodo, "bloque_continuacion", [])
    cuerpo_escape = getattr(nodo, "bloque_escape", [])
    if self.usa_indentacion is None:
        self.usa_indentacion = any(
            hasattr(inst, "variable") for inst in cuerpo_normal + cuerpo_escape
        )
    condicion = self.obtener_valor(nodo.condicion)
    self.agregar_linea(f"if (!({condicion})) {{")
    if self.usa_indentacion:
        self.indentacion += 1
    for instruccion in cuerpo_escape:
        instruccion.aceptar(self)
    if self.usa_indentacion:
        self.indentacion -= 1
    self.agregar_linea("}")
    for instruccion in cuerpo_normal:
        instruccion.aceptar(self)
