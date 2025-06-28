from backend.src.core.ast_nodes import NodoAtributo

def visit_asignacion(self, nodo):
    """Transpila una asignación en JavaScript."""
    if self.usa_indentacion is None:
        self.usa_indentacion = hasattr(nodo, "variable") or hasattr(nodo, "identificador")
    nombre_raw = getattr(nodo, "identificador", getattr(nodo, "variable", None))
    if isinstance(nombre_raw, NodoAtributo):
        nombre = self.obtener_valor(nombre_raw)
        prefijo = ""
    else:
        nombre = nombre_raw
        prefijo = "let " if hasattr(nodo, "variable") else ""
    valor = getattr(nodo, "expresion", getattr(nodo, "valor", None))
    valor = self.obtener_valor(valor)
    self.agregar_linea(f"{prefijo}{nombre} = {valor};")
