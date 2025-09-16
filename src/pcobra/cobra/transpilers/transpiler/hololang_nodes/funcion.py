"""Funciones de Hololang."""

from cobra.transpilers.semantica import procesar_bloque


def visit_funcion(self, nodo):
    """Transpila una función Cobra a Hololang."""
    for decorador in getattr(nodo, "decoradores", []) or []:
        expresion = self.obtener_valor(decorador.expresion)
        self.agregar_linea(f"@{expresion}")
    genericos = f"<{', '.join(nodo.type_params)}>" if getattr(nodo, "type_params", []) else ""
    parametros = ", ".join(nodo.parametros)
    prefijo = "async " if getattr(nodo, "asincronica", False) else ""
    self.agregar_linea(f"{prefijo}fn {nodo.nombre}{genericos}({parametros}) {{")
    procesar_bloque(self, nodo.cuerpo)
    self.agregar_linea("}")
