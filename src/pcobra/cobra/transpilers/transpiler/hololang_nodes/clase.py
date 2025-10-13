"""Clases para Hololang."""

from pcobra.cobra.transpilers.semantica import procesar_bloque


def visit_clase(self, nodo):
    """Transpila la definición de una clase."""
    genericos = f"<{', '.join(nodo.type_params)}>" if getattr(nodo, "type_params", []) else ""
    bases = f" : {', '.join(nodo.bases)}" if getattr(nodo, "bases", []) else ""
    self.agregar_linea(f"class {nodo.nombre}{genericos}{bases} {{")
    procesar_bloque(self, nodo.metodos)
    self.agregar_linea("}")
