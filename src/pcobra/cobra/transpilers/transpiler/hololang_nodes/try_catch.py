"""Bloques try-catch en Hololang."""

from pcobra.cobra.transpilers.semantica import procesar_bloque


def visit_try_catch(self, nodo):
    """Transpila un bloque try/catch/finally."""
    self.agregar_linea("try {")
    procesar_bloque(self, nodo.bloque_try)
    if getattr(nodo, "bloque_catch", []):
        nombre = nodo.nombre_excepcion or "error"
        self.agregar_linea(f"}} catch ({nombre}) {{")
        procesar_bloque(self, nodo.bloque_catch)
    if getattr(nodo, "bloque_finally", []):
        self.agregar_linea("} finally {")
        procesar_bloque(self, nodo.bloque_finally)
    self.agregar_linea("}")
