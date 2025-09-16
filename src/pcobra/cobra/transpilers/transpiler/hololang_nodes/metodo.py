"""Métodos de clase en Hololang."""

from cobra.transpilers.semantica import procesar_bloque


def visit_metodo(self, nodo):
    """Transpila un método perteneciente a una clase."""
    genericos = f"<{', '.join(nodo.type_params)}>" if getattr(nodo, "type_params", []) else ""
    parametros = ", ".join(nodo.parametros)
    prefijo = "async " if getattr(nodo, "asincronica", False) else ""
    self.agregar_linea(f"{prefijo}fn {nodo.nombre}{genericos}({parametros}) {{")
    procesar_bloque(self, nodo.cuerpo)
    self.agregar_linea("}")
