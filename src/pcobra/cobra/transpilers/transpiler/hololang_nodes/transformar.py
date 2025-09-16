"""Transformaciones de holobits para Hololang."""


def visit_transformar(self, nodo):
    """Transpila la instrucción ``transformar``."""
    hb = self.obtener_valor(nodo.holobit)
    operacion = self.obtener_valor(nodo.operacion)
    parametros = ", ".join(self.obtener_valor(p) for p in nodo.parametros)
    if parametros:
        self.agregar_linea(f"transform({hb}, {operacion}, {parametros});")
    else:
        self.agregar_linea(f"transform({hb}, {operacion});")
