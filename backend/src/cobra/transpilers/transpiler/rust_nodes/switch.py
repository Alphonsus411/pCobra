from typing import Any


def visit_switch(self, nodo: Any) -> None:
    expr = self.obtener_valor(nodo.expresion)
    self.agregar_linea(f"match {expr} {{")
    self.indent += 1
    for caso in nodo.casos:
        val = self.obtener_valor(caso.valor)
        self.agregar_linea(f"{val} => {{")
        self.indent += 1
        for inst in caso.cuerpo:
            inst.aceptar(self)
        self.indent -= 1
        self.agregar_linea("},")
    if nodo.por_defecto:
        self.agregar_linea("_ => {")
        self.indent += 1
        for inst in nodo.por_defecto:
            inst.aceptar(self)
        self.indent -= 1
        self.agregar_linea("},")
    self.indent -= 1
    self.agregar_linea("}")
