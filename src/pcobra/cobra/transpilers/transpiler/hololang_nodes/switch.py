"""Estructura ``match`` para Hololang."""


def visit_switch(self, nodo):
    """Transpila una estructura de patrones estilo ``match``."""
    expresion = self.obtener_valor(nodo.expresion)
    self.agregar_linea(f"match {expresion} {{")
    self.indentacion += 1
    for caso in nodo.casos:
        valor = self.obtener_valor(caso.valor)
        self.agregar_linea(f"{valor} => {{")
        self.indentacion += 1
        for instruccion in caso.cuerpo:
            instruccion.aceptar(self)
        self.indentacion -= 1
        self.agregar_linea("},")
    if getattr(nodo, "por_defecto", []):
        self.agregar_linea("_ => {")
        self.indentacion += 1
        for instruccion in nodo.por_defecto:
            instruccion.aceptar(self)
        self.indentacion -= 1
        self.agregar_linea("},")
    self.indentacion -= 1
    self.agregar_linea("};")
