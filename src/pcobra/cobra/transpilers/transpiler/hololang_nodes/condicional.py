"""Nodo condicional para Hololang."""

from pcobra.cobra.transpilers.semantica import procesar_bloque


def visit_condicional(self, nodo):
    """Transpila una estructura condicional a Hololang."""
    cuerpo_si = getattr(nodo, "bloque_si", getattr(nodo, "cuerpo_si", []))
    cuerpo_sino = getattr(nodo, "bloque_sino", getattr(nodo, "cuerpo_sino", []))
    condicion = self.obtener_valor(nodo.condicion)
    self.agregar_linea(f"if ({condicion}) {{")
    procesar_bloque(self, cuerpo_si)
    if cuerpo_sino:
        self.agregar_linea("} else {")
        procesar_bloque(self, cuerpo_sino)
    self.agregar_linea("}")
